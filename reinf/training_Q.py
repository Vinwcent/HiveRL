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
batch_size = 32

agent = Agent(eps=0.2, lr=1e-03, device=device, batch_size=batch_size)
agent.load_models(name="test_6_500", mode="attack")
env = HiveEnv(render_mode=render_mode, mode=mode)
n_episodes = 100
n_models = len(os.listdir("models/attack")) // 2
amount_of_win = 0

n_updates = 0

def convert_state_torch(numpy_array):
    torch_array = convert_numpy_torch(numpy_array)
    torch_array = torch.moveaxis(torch_array, 2, 0)
    return torch_array

def convert_numpy_torch(numpy_array):
    torch_array = torch.Tensor(numpy_array)
    torch_array = torch_array.to(device)
    return torch_array

for episode in range(n_episodes):
    init_state, info = env.reset()
    ally_state = convert_state_torch(init_state)

    done = False
    step = 0
    ally = env.player
    agent.reset_memory()
    while not done and step < batch_size*4:
        # Get amount of pieces blocking enemy bee
        state_blocker = env.get_amount_blocking(ally)

        ally_action, ally_action_tensor = agent.get_play_action(ally_state, env)
        resulting_state, done, _ = env.step(ally_action)

        if resulting_state is not None:
            resulting_state = convert_state_torch(resulting_state)

        while env.player != ally and not done:
            enemy_action, enemy_action_tensor = agent.get_play_action(resulting_state, env)
            resulting_state, done, _ = env.step(enemy_action)
            if resulting_state is not None:
                resulting_state = convert_state_torch(resulting_state)
            step += 1

        # We get the resulting state once the enemy played and compute blocker
        next_ally_state = resulting_state
        next_state_blocker = env.get_amount_blocking(ally)

        next_action_space = env.get_current_action_space()
        next_action_space = convert_numpy_torch(next_action_space)

        if done:
            reward = [100] if env.get_winner() == ally else [-100]
            reward = convert_numpy_torch(reward)
            print(reward[0])
        else:
            reward = [next_state_blocker - state_blocker]
            reward = convert_numpy_torch(reward)

        if next_ally_state is not None:
            agent.memory.push(ally_state[None, ...], ally_action_tensor[None, ...], reward[None, ...], next_ally_state[None, ...], next_action_space)
        else:
            agent.memory.push(ally_state[None, ...], ally_action_tensor[None, ...], reward[None, ...], None, None)



        ally_state = next_ally_state
        step += 1

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




