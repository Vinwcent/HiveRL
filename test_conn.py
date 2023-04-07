from game.GameManager import GameManager
from reinf.MCTS import MCTS
from reinf.Trainer import Trainer
import random
import time
import numpy as np

game_manager = GameManager(with_rendering=True,
                           interactive=False)


Trainer = Trainer(with_rendering=True)

Trainer.train()

#mcts = MCTS()
#mcts.get_policy_vector(game_manager.get_state(), game_manager.turn, game_manager.player)


# for i in range(100):
#     x = random.randint(0, 10)
#     y = 11
#     z = random.randint(0, 6)
#     action_index = [x, y, z]
#     action_space = game_manager.get_legal_connected_action_space()
#     legal_actions = np.argwhere(action_space == 1)
#     print(len(legal_actions))
#     r = random.randint(0, len(legal_actions)-1)
#     action_index = legal_actions[r]
#     game_manager.handle_connected_action(action_index)
#     time.sleep(0.5)
