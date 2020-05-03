import torch
import torch.nn as nn
import torch.nn.functional as F

class QNetwork(nn.Module):
    """
    Policy model
    """

    def __init__(self, state_size, action_size, seed, fc1_units, fc2_units):
        '''
        Build model

        :param state_size : int - Dimension of each state
        :param action_size: int - Dimension of each action
        :param seed: int - Random seed
        :param fc1_units: int - number of nodes in first hidden layer
        :param fc2_units: int - number of nodes in second hidden layer
        '''
        super(QNetwork, self).__init__()
        self.seed = torch.manual_seed(seed)

        # Model
        self.fc1 = nn.Linear(state_size, fc1_units)
        self.fc2 = nn.Linear(fc1_units, fc2_units)
        self.fc3 = nn.Linear(fc2_units, action_size)


    def forward(self, state):
        '''
        Build a network that maps state -> action values
        :param state:
        :return: nn.Linear
        '''
        x = F.relu(self.fc1(state))
        x = F.relu(self.fc2(x))
        return self.fc3(x)
