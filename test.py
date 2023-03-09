from HiveEnv import HiveEnv
import time


env = HiveEnv(render_mode="human")
env.reset()

for i in range(2):
    if i == 0:
        action = [[1, -1, -1],
                  [22, 11, 0]]
    elif i == 1:
        action = [[3, -1, -1],
                  [24, 11, 0]]
    next_state, reward, done, _, _ = env.step(action)
    time.sleep(0.5)

env.game_manager.start_full_interactive
