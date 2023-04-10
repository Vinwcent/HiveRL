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
trainer = Trainer(model_name="train5", net=net, with_rendering=True)
trainer.load_history_and_net("train4", 13)

while True:
    trainer.generate_episode()
trainer.train()
