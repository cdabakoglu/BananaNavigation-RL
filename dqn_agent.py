import numpy as np
import random
from model import QNetwork
import torch
import torch.nn.functional as F
import torch.optim as optim
from dqn_extensions_helper.ReplayBuffer import ReplayBuffer

BUFFER_SIZE = 100000     # replay buffer size
BATCH_SIZE = 64          # mini-batch size
GAMMA = 0.99             # discount rate
TAU = 0.003              # for soft update of target parameters
LR = 0.001               # learning rate
UPDATE_EVERY = 4         # how often to update network

device = torch.device("cuda:0" if torch.cuda.is_available() else "cpu")

class Agent():
    def __init__(self, state_size, action_size, seed, fc1, fc2):
        '''
        Initialize with and learns from the environment

        :param state_size: int - dimension of each state
        :param action_size: int - dimension of each action
        :param seed: int - random seed
        '''

        self.state_size = state_size
        self.action_size = action_size
        self.seed = random.seed(seed)

        # Q-Network
        self.qnetwork_local = QNetwork(state_size, action_size, seed, fc1, fc2).to(device)
        self.qnetwork_target = QNetwork(state_size, action_size, seed, fc1, fc2).to(device)
        self.optimizer = optim.Adam(self.qnetwork_local.parameters(), lr=LR)

        # Replay memory
        self.memory = ReplayBuffer(action_size, BUFFER_SIZE, BATCH_SIZE, seed, device)

        # Initialize time step (for updating every UPDATE_EVERY steps)
        self.time_step = 0


    def step(self, state, action, reward, next_state, done):
        # Save experience in replay memory
        self.memory.add(state, action, reward, next_state, done)

        # Learn every UPDATE_EVERY time steps.
        self.time_step = (self.time_step + 1) % UPDATE_EVERY
        if self.time_step == 0:
            # If enough samples are available in memory, get subset and learn from them
            if len(self.memory) > BATCH_SIZE:
                experiences = self.memory.sample()
                self.learn(experiences, GAMMA)


    def act(self, state, eps=0.0):
        '''
        Returns actions for given state as per current policy

        :param state: array_like - current state
        :param eps: float - epsilon, for epsilon-greedy action selection
        :return: array_like
        '''

        state = torch.from_numpy(state).float().unsqueeze(0).to(device)
        self.qnetwork_local.eval()

        with torch.no_grad():
            action_values = self.qnetwork_local(state)
        self.qnetwork_local.train()

        # Epsilon-greedy action selection
        if random.random() > eps:
            return np.argmax(action_values.cpu().data.numpy())
        else:
            return random.choice(np.arange(self.action_size))


    def learn(self, experiences, gamma):
        '''
        Update value parameters using given batch of experience tuples
        :param experiences: Tuple(torch.Tensor) - tuple of (s, a, r, s', done) tuples
        :param gamma: float - discount rate
        '''

        states, actions, rewards, next_states, dones = experiences

        # Get max predicted Q values (for next states) from target model
        Q_targets_next = self.qnetwork_target(next_states).detach().max(1)[0].unsqueeze(1)

        # Compute Q targets for current states
        Q_targets = rewards + (gamma * Q_targets_next * (1 - dones))

        # Get expected Q values from local model
        Q_expected = self.qnetwork_local(states).gather(1, actions)

        # Compute loss
        loss = F.mse_loss(Q_expected, Q_targets)

        # Minimize the loss
        self.optimizer.zero_grad()
        loss.backward()
        self.optimizer.step()

        # Update target network
        self.soft_update(self.qnetwork_local, self.qnetwork_target, TAU)


    def soft_update(self, local_model, target_model, tau):
        '''
        Soft update model parameters
        θ_target = τ*θ_local + (1 - τ)*θ_target
        :param local_model: - pytorch model - weights will be copied from
        :param target_model: - pytorch model - weights will be copied to
        :param tau: float - interpolation parameter
        '''
        for target_param, local_param in zip(target_model.parameters(), local_model.parameters()):
            target_param.data.copy_(tau * local_param.data + (1.0 - tau) * target_param.data)
