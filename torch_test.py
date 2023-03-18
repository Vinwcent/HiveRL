import gymnasium as gym
import time
import random
import math
import numpy as np
from collections import namedtuple, deque
from HiveEnv import HiveEnv

import torch
import torch.nn as nn
import torch.optim as optim
import torch.nn.functional as F

device = torch.device("mps")

env = HiveEnv(render_mode="human")

## Memory

Transition = namedtuple("Transition",
                        ("state", "action",
                         "reward", "next_state",
                         "next_action_space"))

class ReplayMemory(object):

    def __init__(self, capacity):
        self.memory = deque([], maxlen=capacity)

    def push(self, *args):
        self.memory.append(Transition(*args))

    def sample(self, batch_size):
        return random.sample(self.memory, batch_size)

    def __len__(self):
        return len(self.memory)

## Q-network

class DQN(nn.Module):

    def __init__(self):
        super(DQN, self).__init__()
        self.conv1 = nn.Conv2d(5, 16, 2)
        self.conv2 = nn.Conv2d(16, 32, 3, (2, 1))

        self.action_flattener = nn.Flatten()
        self.linear_action_1 = nn.Linear(6, 21*19)

        self.conv3 = nn.Conv2d(33, 64, 3)
        self.conv4 = nn.Conv2d(64, 128, 3)
        self.conv5 = nn.Conv2d(128, 256, 3)

        self.value_flattener = nn.Flatten()
        self.end_linear_1 = nn.Linear(49920, 256)
        self.end_linear_2 = nn.Linear(256, 1)

    def forward(self, state, action):
        state = self.conv1(state)
        state = self.conv2(state)

        action = self.action_flattener(action)
        action = self.linear_action_1(action)
        action = action.view((-1, 1, 21, 19))

        value = torch.cat((state, action), 1)
        value = self.conv3(value)
        value = self.conv4(value)
        value = self.conv5(value)

        value = self.value_flattener(value)
        value = self.end_linear_1(value)
        value = self.end_linear_2(value)

        return value

# test = DQN()
#  st = np.random.randint(low=0, high=5, size=(5, 43, 22))
#  ac = np.array([[0, 0, 0],
#                 [0, 0, 0]])
# 
# st = torch.tensor(st, dtype=torch.float32)
# st = torch.reshape(st, (1, 5, 43, 22))
# 
# ac = torch.tensor(ac, dtype=torch.float32)
# ac = torch.reshape(ac, (1, 1, 2, 3))
# 
# print(st.shape, ac.shape)
# 
# value = test(st, ac)
# 
# print(value.shape)

BATCH_SIZE = 128
GAMMA = 0.99
LEARNING_RATE = 1e-4
EPS = 0.9

policy_net = DQN().to(device)
target_net = DQN().to(device)

target_net.load_state_dict(policy_net.state_dict())

optimizer = optim.AdamW(policy_net.parameters(), lr=LEARNING_RATE, amsgrad=True)
memory = ReplayMemory(10000)

def get_greedy_action_index(state, action_space, net):
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

def select_action_index(state, action_space, net):
    '''
    state: Tensor
    action_space: Tensor

    Compute the index of the next action
    '''
    if random.random() < EPS:
        exploration_index = random.randint(0, action_space.shape[0]-1)
        print("EXPLOOOO")
        return exploration_index
    else:
        exploitation_index = get_greedy_action_index(state, action_space, net)
        return exploitation_index

def select_action(state, env):
    '''
    Select the next action to play
    '''
    action_space_numpy = env.get_current_action_space()

    action_space_torch = torch.Tensor(action_space_numpy)
    action_space_torch = action_space_torch.to(device)
    index = select_action_index(state, action_space_torch, policy_net)

    return action_space_numpy[index], action_space_torch[index]




# st = np.random.randint(low=0, high=5, size=(5, 43, 22))
# ac = np.array([[[0, 0, 0],
#               [0, 0, 0]],
#              [[1, 1, 1],
#               [1, 1, 1]]])
# st = torch.tensor(st, dtype=torch.float32)
# st = st.to(device)
# st = torch.reshape(st, (1, 5, 43, 22))
# 
# ac = torch.tensor(ac, dtype=torch.float32)
# ac = ac.to(device)
# ac = torch.reshape(ac, (2, 2, 3))
# 
# select_action(st, ac)

def update_network():
    '''
    Update the network by sampling in experiences
    '''
    # We check if we played enough to update
    if len(memory) < BATCH_SIZE:
        return

    # [(s1, a1, r1, s1_), (s2, a2...)] to [(s1, s2..), (a1, a2...), (r1, r2...), (s1_, s2_..)]
    transitions = memory.sample(BATCH_SIZE)
    batch = Transition(*zip(*transitions))

    batch_state = torch.cat(batch.state)
    batch_action = torch.cat(batch.action)
    batch_reward = torch.cat(batch.reward)
    batch_next_state = torch.cat(batch.next_state)

    # Compute the best actions available in the action space for target net
    next_action_state_pair = zip(batch.next_state, batch.next_action_space)
    batch_next_actions = torch.Tensor([])
    batch_next_actions = batch_next_actions.to(device)
    for next_state, action_space in next_action_state_pair:
        index = get_greedy_action_index(next_state, action_space, target_net)
        best_action = action_space[index].reshape(-1, *action_space[index].shape)
        batch_next_actions = torch.cat([batch_next_actions, best_action])

    # Compute the state action values tensor
    state_action_values = policy_net(batch_state, batch_action)

    with torch.no_grad():
        next_state_action_values = target_net(batch_next_state, batch_next_actions)

    print((next_state_action_values * GAMMA).shape)
    expected_value = (next_state_action_values * GAMMA) + batch_reward[:, None]
    criterion = nn.SmoothL1Loss()
    loss = criterion(state_action_values, expected_value)

    optimizer.zero_grad()
    loss.backward()
    optimizer.step()

    # Compute the value of the best next action


n_episodes = 1000

done = False
for episode in range(n_episodes):
    state, info = env.reset()
    state = torch.Tensor(state)
    state = state.to(device)
    state = torch.moveaxis(state, 2, 0)
    step = 0
    while not done and step<100:
        # Get information about environment in numpy version
        try:
            action, action_tensor = select_action(state, env)
            next_state, reward, done, _, _ = env.step(action)
        except:
            break


        # Get reward and next_state in tensor version
        reward = torch.tensor(reward)
        reward = reward.to(device)
        if done:
            next_state = None
        else:
            next_state = torch.Tensor(next_state)
            next_state = next_state.to(device)
            next_state = torch.moveaxis(next_state, 2, 0)

        # Compute the action space and store it with all informations for replay
        next_action_space_numpy = env.get_current_action_space()
        next_action_space = torch.Tensor(next_action_space_numpy)
        next_action_space = next_action_space.to(device)
        memory.push(state[None, ...], action_tensor[None, ...], reward[None, ...], next_state[None, ...], next_action_space)


        state = next_state
        step += 1






































































































