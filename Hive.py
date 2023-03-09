import numpy as np
import pygame as pg

import gymnasium as gym

class Hive(gym.Env):
    metadata = {"render_mods": ["human", "None"],
                "render_fps": 1}

    def __init__(self, render_mode=None):
        '''
        Create a hive environment
        '''

