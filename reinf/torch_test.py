import gymnasium as gym
import time
import random
import math
import numpy as np
import time

# Modify the path to work from main folder
import sys, os
sys.path.insert(0, os.getcwd())

from reinf.HiveEnv import HiveEnv
from reinf.networks import DQN, NetworkManager
from reinf.memory import ReplayMemory, Transition
from reinf.Agent import Agent

from termcolor import colored

import torch
import torch.nn as nn
import torch.optim as optim
import torch.nn.functional as F

device = torch.device("mps")

mode = "attack"
training = False
render_mode = "human"

agent = Agent(eps=1.0, lr=1e-03, device=device, batch_size=32)
#agent.load_models(name="test_1_200", mode="attack")


env = HiveEnv(render_mode=render_mode, mode=mode)
n_episodes = 100000
amount_of_win = 0

n_models = len(os.listdir("models/attack")) // 2
n_updates = 0
step = 0


for episode in range(n_episodes):
    state, info = env.reset()
    state = torch.Tensor(state)
    state = state.to(device)
    state = torch.moveaxis(state, 2, 0)

    done = False
    step = 0
    while not done:
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

        if done:
            print("Game ended")

        updated = 0
        if training:
            updated = agent.update_policy_network()
        if updated == 1:
            n_updates += 1
            if n_updates % 10 == 0:
                text = colored(f"Remaining until save {100 - n_updates % 100}", "yellow")
                print(text)

            if n_updates % 100 == 0:
                agent.save_models(f"test_{n_models+1}_{n_updates}", mode=mode)
                text = colored("Model Saved", "red")
                print(text)






































































































