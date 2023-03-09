from HiveEnv import HiveEnv
import time
import random


env = HiveEnv(render_mode="human")
env.reset()

for i in range(1000):
    action_space = env.game_manager.get_legal_action_space()
    action = random.choice(action_space)
    print(action)
    next_state, reward, done, _, _ = env.step(action)
    time.sleep(0.01)

env.game_manager.start_full_interactive
