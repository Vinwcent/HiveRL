import gymnasium as gym
import time
import random
import math
import numpy as np

# Modify the path to work from main folder
import sys, os
sys.path.insert(0, os.getcwd())

from reinf.HiveEnv import HiveEnv
from reinf.networks import DQN, NetworkManager
from reinf.memory import ReplayMemory, Transition
from reinf.Agent import Agent

import torch
import torch.nn as nn
import torch.optim as optim
import torch.nn.functional as F

device = torch.device("mps")
env = HiveEnv(render_mode="human", mode="attack")

agent = Agent(eps=0.2, lr=1e-05, device=device)
agent.load_models("test_1_100", "attack")
training = True
n_episodes = 100000
amount_of_win = 0

n_models = len(os.listdir("models/attack")) // 2
n_updates = 0
step = 0

for episode in range(n_episodes):
    done = False
    state, info = env.reset()
    state = torch.Tensor(state)
    state = state.to(device)
    state = torch.moveaxis(state, 2, 0)
    if step >= 200:
        step = 0
        agent.reset_memory()
    while not done and step<200:
        # Get information about environment in numpy version
        try:
            action, action_tensor = agent.get_play_action(state, env)
            next_state, enemy_game_state, reward, done, _ = env.step(action)
        except:
            break


        # Get reward and next_state in tensor version
        reward = torch.tensor(reward)
        reward = reward.to(device)
        if next_state is not None:
            next_state = torch.Tensor(next_state)
            next_state = next_state.to(device)
            next_state = torch.moveaxis(next_state, 2, 0)


        # Compute the action space and store it with all informations for replay
        next_action_space_numpy = env.get_current_action_space()
        next_action_space = torch.Tensor(next_action_space_numpy)
        next_action_space = next_action_space.to(device)

        if next_state is not None:
            agent.memory.push(state[None, ...], action_tensor[None, ...], reward[None, ...], next_state[None, ...], next_action_space)
        else:
            agent.memory.push(state[None, ...], action_tensor[None, ...], reward[None, ...], None, None)


        if enemy_game_state is not None:
            state = enemy_game_state
            state = torch.Tensor(state)
            state = state.to(device)
            state = torch.moveaxis(state, 2, 0)
            step += 1

        updated = 0
        if training:
            updated = agent.update_policy_network()
        if updated == 1:
            n_updates += 1
            if n_updates % 10 == 0:
                print(f"Remaining until save {100 - n_updates % 1500}")

            if n_updates % 1500 == 0:
                agent.save_models(f"test_{n_models+1}_{n_updates}", mode="attack")
                print("Model saved")






































































































