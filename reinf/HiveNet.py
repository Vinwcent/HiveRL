import numpy as np
import os

import torch
import torch.optim as optim
from tqdm import tqdm


from reinf.Net import Net
class HiveNet():
    def __init__(self, device):
        self.device = device
        self.raw_net = Net().to(device)

        self.losses = []

    def torch_converter(self, tensor):
        float_tensor = np.array(tensor).astype(np.float64)
        torch_tensor = torch.FloatTensor(float_tensor)
        torch_tensor = torch_tensor.to(self.device)
        return torch_tensor

    def loss_probs(self, target, pred):
        return -torch.sum(target * pred) / target.size()[0]

    def loss_values(self, target, pred):
        '''
        MSE
        '''
        return torch.sum((target - pred.view(-1)) ** 2) / target.size()[0]



    def train(self, samples, n_epochs, batch_size=32):
        '''
        Train the neural net with list of examples in the form (state, probs, value)
        '''

        optimizer = optim.Adam(self.raw_net.parameters())

        for epoch in range(1, n_epochs + 1):
            print(f"EPOCH: {epoch}")
            # Training mode for dropout
            self.raw_net.train()
            probs_losses = AverageMeter()
            value_losses = AverageMeter()

            n_batch = int(len(samples)/batch_size)

            loading_bar = tqdm(range(n_batch), desc="Training")
            for _ in loading_bar:
                indexes = np.random.randint(len(samples), size=batch_size)
                # [[s1, p1, v1], ...] to [[s1, s2, ..], [p1, p2, ..]]
                states, probs, values = list(zip(*[samples[i] for i in range(len(samples))]))
                # Convert to torch
                states = self.torch_converter(states)
                probs = self.torch_converter(probs)
                values = self.torch_converter(values)

                pred_probs, pred_values = self.raw_net(states)
                loss_probs = self.loss_probs(probs, pred_probs)
                loss_values = self.loss_values(values, pred_values)
                loss = loss_probs + loss_values


                probs_losses.update(loss_probs.item())
                value_losses.update(loss_values.item())
                loading_bar.set_postfix({"L_probs":probs_losses,
                                         "L_values":value_losses})

                optimizer.zero_grad()
                loss.backward()
                optimizer.step()
            self.losses.append([probs_losses, value_losses])

    def predict(self, state):
        '''
        Predict the probs and value associated to state and return the numpy version of them
        '''

        torch_state = self.torch_converter(state)
        # Eval mode for dropout
        self.raw_net.eval()
        with torch.no_grad():
            probs, value = self.raw_net(torch_state)
        return torch.exp(probs).data.cpu().numpy()[0], value.data.cpu().numpy()[0]

    def save_ckpt(self, folder="models", filename="checkpoint.pth.tar"):
        filepath = os.path.join(folder, filename)
        torch.save({
            'state_dict': self.raw_net.state_dict(),
            'losses': self.losses
        }, filepath)

    def load_ckpt(self, folder="models", filename="checkpoint.pth.tar"):
        filepath = os.path.join(folder, filename)
        checkpoint = torch.load(filepath, map_location=torch.device('mps'))
        self.losses = checkpoint['losses']
        self.raw_net.load_state_dict(checkpoint['state_dict'])


class AverageMeter(object):
    """From https://github.com/pytorch/examples/blob/master/imagenet/main.py"""

    def __init__(self):
        self.val = 0
        self.avg = 0
        self.sum = 0
        self.count = 0

    def __repr__(self):
        return f'{self.avg:.2e}'

    def update(self, val, n=1):
        self.val = val
        self.sum += val * n
        self.count += n
        self.avg = self.sum / self.count


class dotdict(dict):
    def __getattr__(self, name):
        return self[name]
