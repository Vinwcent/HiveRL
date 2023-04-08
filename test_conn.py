from game.GameManager import GameManager
from reinf.MCTS import MCTS
from reinf.Trainer import Trainer
import random
import time
import numpy as np

import torch

from reinf.HiveNet import HiveNet


device = torch.device("mps")
net = HiveNet(device)
trainer = Trainer(model_name="test3", net=net, with_rendering=False)
trainer.load_history_and_net("test2", 7)


trainer.train()

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
