import random

import torch
import torch.nn as nn
import torch.optim as optim
import torch.nn.functional as F

class ResBlock(nn.Module):
    def __init__(self, in_channels, out_channels, stride=1):
        super(ResBlock, self).__init__()
        self.conv1 = nn.Sequential(nn.Conv2d(in_channels, out_channels, kernel_size=3, stride=stride, padding=1),
                                   nn.BatchNorm2d(out_channels),
                                   nn.ReLU())
        self.conv2 = nn.Sequential(nn.Conv2d(out_channels, out_channels, kernel_size=3, stride=1, padding=1),
                                   nn.BatchNorm2d(out_channels))
        self.relu = nn.ReLU()

        self.downsampler = nn.Sequential(
            nn.Conv2d(in_channels, out_channels, kernel_size=1, stride=stride),
            nn.BatchNorm2d(out_channels))

        self.stride = stride



    def forward(self, x):
        residual = x
        output = self.conv1(x)
        output = self.conv2(output)
        residual = self.downsampler(residual)
        output += residual
        output = self.relu(output)
        return output


class DQN(nn.Module):

    def __init__(self):
        super(DQN, self).__init__()
        self.conv1 = nn.Conv2d(10, 32, 2)
        self.action_flattener = nn.Flatten()
        self.linear_action_1 = nn.Linear(6, 44*21)

        self.block1 = ResBlock(33, 64, stride=2)
        self.block2 = ResBlock(64, 128, stride=2)
        self.block3 = ResBlock(128, 256, stride=1)
        self.block4 = ResBlock(256, 512, stride=2)

        self.value_flattener = nn.Flatten()
        self.end_linear_1 = nn.Linear(9216, 512)
        self.end_linear_2 = nn.Linear(512, 1)

    def forward(self, state, action):
        state = self.conv1(state)


        action = self.action_flattener(action)
        action = self.linear_action_1(action)
        action = action.view((-1, 1, 44, 21))

        value = torch.cat((state, action), 1)
        value = self.block1(value)
        value = self.block2(value)
        value = self.block3(value)
        value = self.block4(value)

        value = self.value_flattener(value)
        value = self.end_linear_1(value)
        value = self.end_linear_2(value)

        return value

class NetworkManager:

    def __init__(self, eps, device):
        self.eps = eps
        self.device = device

    def get_greedy_action_index(self, state, action_space, net):
        '''
        state: Tensor
        action_space: Tensor

        Compute the greedy action index in action space that net in state would take
        '''
        state = state.repeat(action_space.shape[0], 1, 1, 1)
        with torch.no_grad():
            values = net(state, action_space)
            index = torch.argmax(values)
            return index

    def select_action_index(self, state, action_space, net):
        '''
        state: Tensor
        action_space: Tensor

        Compute the index of the next action
        '''
        if random.random() < self.eps:
            exploration_index = random.randint(0, action_space.shape[0]-1)
            return exploration_index
        else:
            exploitation_index = self.get_greedy_action_index(state, action_space, net)
            return exploitation_index

    def select_action(self, state, env, net):
        '''
        Select the next action to play
        '''
        action_space_numpy = env.get_current_action_space()

        action_space_torch = torch.Tensor(action_space_numpy)
        action_space_torch = action_space_torch.to(self.device)
        index = self.select_action_index(state, action_space_torch, net)

        return action_space_numpy[index], action_space_torch[index]
