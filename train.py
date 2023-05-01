from game.GameManager import GameManager
from reinf.MCTS import MCTS
from reinf.Trainer import Trainer
import random
import time
import numpy as np

import torch

from reinf.HiveNet import HiveNet


device = torch.device("cuda")
net = HiveNet(device)
trainer = Trainer(model_name="Unknown",
                  net=net,
                  with_rendering=True)
trainer.load_history_and_net("training", 15)

# trainer.train()
trainer.start_play()
