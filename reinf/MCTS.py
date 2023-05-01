import numpy as np
import math
import time

from game.GameManager import GameManager
from game.Utilities import name_dic

EPS = 1e-8


class MCTS():
    """
    Class used to perform MCTS from a given state
    """

    def __init__(self, net, n_search, max_depth, boost=False):
        self.net = net
        self.boost = boost

        # Headless game manager to make MCTS
        self.game_manager = GameManager(with_rendering=True)

        self.reset_tree()

        self.n_search = n_search
        # Contrary to go, a state can reoccur so we seed a limit depth not to loop in a series of state during the monte carlo search
        self.max_depth = max_depth

        self.cpuct = 1

        all_actions = [[x, y, z]
                       for x in range(11)
                       for y in range(22)
                       for z in range(7)]

    def reset_tree(self):
        self.Q_values = {}
        self.N_s_counts = {}
        self.N_sa_counts = {}
        self.end_values = {}
        self.P = {}
        self.V = {}

    def get_policy_vector(self, state, seen_states, turn, player, temperature=1):
        for i in range(self.n_search):
            if turn == 1:
                self.game_manager.first_bug_placed = None
            self.game_manager.load_state(state, turn, player)
            self._perform_tree_search(state, turn, seen_states, self.max_depth)

        s = self._hash(state)
        visit_counts = np.zeros((11, 22, 7))
        for a in self.game_manager.possible_connected_actions:
            if (s, *a) in self.N_sa_counts:
                visit_counts[(*a,)] = self.N_sa_counts[(s, *a)]



        # Only best action if temperature equal 0
        if temperature == 0:
            best_actions_index = np.argwhere(visit_counts == np.max(visit_counts))
            index = np.random.choice(len(best_actions_index))
            best_action_index = best_actions_index[index]

            probs = np.zeros((11, 22, 7))
            probs[(*best_action_index,)] = 1
            return probs

        visit_counts = visit_counts**(1./temperature)
        visit_counts_sum = float(np.sum(visit_counts))
        probs = visit_counts / visit_counts_sum
        return probs

    def _perform_tree_search(self, state, turn, seen_states, max_depth=100, depth=1, tree_previous_trans={}):
        """
        Perform a tree search recursively without redoing the same actions
        """
        s = self._hash(state)

        # Check if end state
        if s not in self.end_values:
            self.end_values[s] = self.game_manager.get_end_value()

        # End game if end state
        if self.end_values[s] != 0:
            return -self.end_values[s]


        # Policy of s is unknown so init with network
        if s not in self.P:
            self.P[s], value = self.net.predict(state)


            # Boost for the beginning
            if self.boost:
                indexes_far_from_bee = []
                for bug_index in range(11):
                    if 12 not in state[bug_index]:
                        indexes_far_from_bee.append(bug_index)

                self.P[s][indexes_far_from_bee, 11, :] = 1000

            valids = self.game_manager.get_legal_connected_action_space()


            sum_probs = np.sum(self.P[s])
            self.P[s] /= sum_probs

            self.V[s] = valids
            self.N_s_counts[s] = 0


            return -value
        valids = self.V[s]
        if turn == 5 or turn == 6:
            valids = self.game_manager.get_legal_connected_action_space()

        best_value = -float('inf')
        best_action_index = [0, 0, 0]


        for a in self.game_manager.possible_connected_actions:
            if valids[(*a,)]:
                # We prevent redoing a (s, a) couple not to loop during MCTS
                if s in tree_previous_trans and tree_previous_trans[s] == a:
                    continue

                if (s, *a) in self.Q_values:
                    u = self.Q_values[(s, *a)] + self.cpuct * self.P[s][(*a,)] * math.sqrt(self.N_s_counts[s]) / (1 + self.N_sa_counts[(s, *a)])
                else:
                    u = self.cpuct * self.P[s][(*a,)] * math.sqrt(self.N_s_counts[s] + EPS)
                if u > best_value:
                    best_value = u
                    best_action_index = a

        tree_previous_trans[s] = a

        current_player = self.game_manager.player
        next_state, next_player, next_turn = self.game_manager.handle_connected_action(best_action_index)

        # We remove the played transitions to avoid infinite loop
        for seen_state in seen_states:
            if np.array_equal(seen_state, next_state):
                self.V[s][(*best_action_index,)] = 0

        if depth >= max_depth:
            return -best_value if current_player != next_player else best_value

        value = self._perform_tree_search(next_state, next_turn, seen_states, max_depth, depth+1)

        a = best_action_index
        if (s, *a) in self.Q_values:
            self.Q_values[(s, *a)] = (self.N_sa_counts[(s, *a)] * self.Q_values[(s, *a)] + value) / (self.N_sa_counts[(s, *a)] + 1)
            self.N_sa_counts[(s, *a)] += 1
        else:
            self.Q_values[(s, *a)] = value
            self.N_sa_counts[(s, *a)] = 1

        self.N_s_counts[s] += 1
        return -value if current_player != next_player else value



    def _hash(self, state):
        hashed_state = "".join(str(connection) for piece in range(22) for connection in state[piece])
        return hashed_state


