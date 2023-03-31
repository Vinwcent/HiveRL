import numpy as np
import pygame as pg
import gymnasium as gym
import os, sys
from gymnasium import spaces
from game.GameManager import GameManager

class HiveEnv(gym.Env):
    metadata = {"render_mode": ["human", "None"],
                "render_fps": 1}

    def __init__(self, render_mode=None, mode=None):
        '''
        Create a hive environment
        '''

        self.observation_space = spaces.Dict(
            {
                "board_state": spaces.Box(low=0,
                                          high=4,
                                          shape=(45, 22, 5),
                                          dtype=int)
            }
        )
        # Action space is a start_pos_piece to end_pos_piece space
        # [X, -1, -1] start_pos_piece are special actions to add
        # a new piece
        self.action_space = gym.spaces.Box(low=np.array([[0, -1, -1],
                                                         [0, 0, 0]]),
                                           high=np.array([[45, 22, 5],
                                                          [45, 22, 5]]),
                                           dtype=int)

        assert render_mode is None or render_mode in self.metadata["render_mode"]
        self.render_mode = render_mode
        self.game_manager = None
        self.player = None
        self.mode = mode


    def reset(self, seed=None, options=None):
        super().reset(seed=seed)

        with_rendering = self.render_mode == "human"
        self.game_manager = GameManager(interactive=False,
                                        with_rendering=with_rendering)
        self.player = self.game_manager.player

        game_state, info = self.game_manager.get_state_info()

        return game_state, info

    def step(self, action):

        # Get the next state for the current player and the reward associated to
        # the transition to this state
        next_state, info = self.game_manager.handle_RL_action(action, self.mode)
        self.player = self.game_manager.player

        # We check if the game is ended
        is_terminated = self.game_manager.winner != 0

        # Signal to see that the game is finished
        if is_terminated:
            next_state = None

        return next_state, is_terminated, info

    def get_current_action_space(self):
        return self.game_manager.get_legal_action_space()

    def get_action_space_from(self, state):
        dummy_game_manager = GameManager(interactive=False,
                                        with_rendering=False)

    def get_amount_blocking(self, player):
        return self.game_manager.get_amount_blocking_bee(player)

    def get_winner(self):
        return self.game_manager.winner


