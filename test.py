from HiveNet import HiveNet
import numpy as np
import torch


# Create an instance of Net
device = torch.device("mps")
net = HiveNet(device=device)

# Feed it with an example image
example_state = torch.randn(22, 7)

def create_table(n):
    table = []
    for i in range(n):
        table.append((np.zeros((22,7)), np.ones((11,22,7)), np.float64(1)))
    return table

table = create_table(1000)

probs, value = net.predict(example_state)
print(probs.shape, value)

