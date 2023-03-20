from reinf.networks import DQN, NetworkManager
from reinf.memory import ReplayMemory, Transition

import torch
import torch.nn as nn
import torch.optim as optim
import torch.nn.functional as F

class Agent:

    def __init__(self,
                 device,
                 lr=1e-04,
                 gamma=0.99,
                 eps=1.0,
                 memory_size=10000,
                 batch_size=128,
                 tau=0.005):

        self.device = device

        self.lr = lr
        self.gamma = gamma
        self.eps = eps
        self.batch_size = batch_size
        self.tau = tau
        self.memory_size = memory_size

        self.memory = ReplayMemory(memory_size)

        self.policy_net = DQN().to(self.device)
        self.target_net = DQN().to(self.device)
        self.target_net.load_state_dict(self.policy_net.state_dict())
        self.network_manager = NetworkManager(self.eps, self.device)
        self.optimizer = optim.AdamW(self.policy_net.parameters(), lr=lr, amsgrad=True)

    def update_policy_network(self):
        '''
        Update the policy network with deep TD by sampling in experiences
        '''
        # We check if we played enough to update
        if len(self.memory) < self.batch_size:
            return 0

        # [(s1, a1, r1, s1_), (s2, a2...)] to [(s1, s2..), (a1, a2...), (r1, r2...), (s1_, s2_..)]
        transitions = self.memory.sample(self.batch_size)
        batch = Transition(*zip(*transitions))

        batch_state = torch.cat(batch.state)
        batch_action = torch.cat(batch.action)
        batch_reward = torch.cat(batch.reward)

        non_final_mask = torch.tensor(tuple(map(lambda s:s is not None,
                                                batch.next_state)), dtype=torch.bool)
        non_final_mask.to(self.device)

        non_final_next_states = [s
                                 for s in batch.next_state
                                 if s is not None]
        non_final_next_action_space = [action_space
                                       for action_space in batch.next_action_space
                                       if action_space is not None]


        # Compute the best actions available in the action space for target net
        next_action_state_pair = zip(non_final_next_states, non_final_next_action_space)
        non_final_next_actions = torch.Tensor([])
        non_final_next_actions = non_final_next_actions.to(self.device)
        for next_state, action_space in next_action_state_pair:
            index = self.network_manager.get_greedy_action_index(next_state, action_space, self.target_net)
            best_action = action_space[index].reshape(-1, *action_space[index].shape)
            non_final_next_actions = torch.cat([non_final_next_actions, best_action])

        non_final_next_states = torch.cat(non_final_next_states)
        non_final_next_states = non_final_next_states.to(self.device)


        # Compute the state action values tensor
        state_action_values = self.policy_net(batch_state, batch_action).squeeze()

        next_state_action_values = torch.zeros(self.batch_size)
        next_state_action_values = next_state_action_values.to(self.device)
        with torch.no_grad():
            next_state_action_values[non_final_mask] = self.target_net(non_final_next_states, non_final_next_actions).squeeze()

        expected_value = (next_state_action_values * self.gamma) + batch_reward

        criterion = nn.SmoothL1Loss()
        loss = criterion(state_action_values, expected_value)

        self.optimizer.zero_grad()
        loss.backward()
        self.optimizer.step()


        self._update_target_network()

        print(f"Loss was {loss}")

        return 1

    def get_play_action(self, state, env):
        action, action_tensor = self.network_manager.select_action(state, env, self.policy_net)
        return action, action_tensor


    def _update_target_network(self):
        '''
        Update the target network weights to make them tau % more like those of the policy net
        '''
        target_state_dict = self.target_net.state_dict()
        policy_state_dict = self.policy_net.state_dict()

        for key in policy_state_dict:
            target_state_dict[key] = policy_state_dict[key]*self.tau + target_state_dict[key] * (1-self.tau)

        self.target_net.load_state_dict(target_state_dict)


    def save_models(self, name, mode):
        torch.save(self.policy_net.state_dict(), f"models/{mode}/policy_{name}")
        torch.save(self.policy_net.state_dict(), f"models/{mode}/target_{name}")

    def load_models(self, name, mode):
        self.policy_net.load_state_dict(torch.load(f"models/{mode}/policy_{name}"))
        self.target_net.load_state_dict(torch.load(f"models/{mode}/target_{name}"))

    def reset_memory(self):
        self.memory = ReplayMemory(self.memory_size)
