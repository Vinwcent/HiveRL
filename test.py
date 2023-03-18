from HiveEnv import HiveEnv
import time
import random
import numpy as np


env = HiveEnv(render_mode="human")
env.reset()

for i in range(10000):
    action_space = env.game_manager.get_legal_action_space()
    print(np.array(action_space).shape)
    action = random.choice(action_space)
    next_state, reward, done, _, _ = env.step(action)

env.game_manager.start_full_interactive()
