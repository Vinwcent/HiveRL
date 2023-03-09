import numpy as np
import pygame as pg
import gymnasium as gym

from gymnasium import spaces
from GameManager import GameManager

class HiveEnv(gym.Env):
    metadata = {"render_mode": ["human", "None"],
                "render_fps": 1}

    def __init__(self, render_mode=None):
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


    def reset(self, seed=None, options=None):
        super().reset(seed=seed)

        with_rendering = self.render_mode == "human"
        self.game_manager = GameManager(interactive=False,
                                        with_rendering=with_rendering)

        game_state, info = self.game_manager.get_state_info()

        return game_state, info

    def step(self, action):

        self.game_manager.handle_RL_action(action)
        is_terminated = self.game_manager.finish
        reward = 1
        game_state, info = self.game_manager.get_state_info()

        return game_state, reward, is_terminated, False, info
