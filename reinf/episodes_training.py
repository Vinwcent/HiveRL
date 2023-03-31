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

import torch
import torch.nn as nn
import torch.optim as optim
import torch.nn.functional as F

device = torch.device("mps")

agent = Agent(eps=0.2, lr=1e-04, device=device, batch_size=256)
agent.load_models(name="test_1_100", mode="bad_reward")
training = False
render_mode = "human"
mode = "bad_reward"
env = HiveEnv(render_mode=render_mode, mode=mode)
n_episodes = 100000
amount_of_win = 0

n_models = len(os.listdir("models/bad_reward")) // 2
n_updates = 0
step = 0

has_won = False

for episode in range(n_episodes):
    state, info = env.reset()
    state = torch.Tensor(state)
    state = state.to(device)
    state = torch.moveaxis(state, 2, 0)
    done = False


    if step >= 257:
        step = 0
        has_won = False
        step = 0
        agent.reset_memory()
    while not done and step < 257:
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
            has_won = True



    if not done:
        print(f"Episode {episode} finished")
    else:
        print(f"Episode {episode} finished with a WIN")


    # Updates only when a game was win
    if not has_won or step < 257:
        continue

    for _ in range(50):
        agent.update_policy_network()
        n_updates += 1
        if n_updates % 10 == 0:
            print(f"Remaining until save {100 - n_updates % 100}")

        if n_updates % 100 == 0:
            agent.save_models(f"test_{n_models+1}_{n_updates}", mode=mode)
            print("Model saved")






































































































