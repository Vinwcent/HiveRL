import numpy as np

from reinf.MCTS import MCTS
from game.GameManager import GameManager

from tqdm import tqdm
from collections import deque

class Trainer():
    """
    Class used to make the training of the reinforcement agent
    """

    def __init__(self, with_rendering):
        self.with_rendering = with_rendering
        self.mcts = MCTS()

        self.history = []
        self.length_history = 100

    def generate_episode(self):
        """
        Create an episode
        """
        episode_steps = []
        game_manager = GameManager(interactive=False,
                                   with_rendering=self.with_rendering)

        step = 0
        while True:
            step += 1
            temperature = 1 if step < 20 else 0

            state = game_manager.get_state()
            player = game_manager.player
            turn = game_manager.turn
            probs_array = self.mcts.get_policy_vector(state,
                                                      turn,
                                                       player,
                                                       temperature)
            episode_steps.append([state, player, turn, probs_array, None])
            possibles_actions = np.argwhere(probs_array > 0)
            possibles_actions_probs = probs_array[possibles_actions[:, 0],
                                                  possibles_actions[:, 1],
                                                  possibles_actions[:, 2]]
            index = np.random.choice(len(possibles_actions), p=possibles_actions_probs)
            action = possibles_actions[index]


            state, player, turn = game_manager.handle_connected_action(action)

            reward = game_manager.get_end_value()

            if reward != 0:
                return [(step[0], step[3], reward * (-1) ** (step[1] != player)) for step in episode_steps]

    def train(self):

        num_episodes = 10

        for i in range(1, 1000):
            episodes = deque([], maxlen=10000)

            for _ in tqdm(range(num_episodes), desc="Generating games"):
                self.mcts.reset_tree()
                episodes += self.generate_episode()

            self.history += episodes
            if len(self.history) > self.length_history:
                self.history.pop(0)








