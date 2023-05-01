import numpy as np
import os
import sys

from reinf.MCTS import MCTS
from game.GameManager import GameManager
from pickle import Pickler, Unpickler
from random import shuffle

from tqdm import tqdm
from collections import deque
from termcolor import colored

class Trainer():
    """
    Class used to make the training of the reinforcement agent
    """

    def __init__(self,
                 model_name,
                 net,
                 mc_search=10,
                 mc_depth=30,
                 with_rendering=True):

        self.with_rendering = with_rendering

        self.net = net
        self.gen_mcts = MCTS(net, mc_search, mc_depth, boost=True)
        self.compet_net = None

        self.model_name = model_name

        self.history = []

    def rotate(self, state, probs_array, amount):
        '''
        Rotate state and corresponding probs to handle rotation
        '''
        new_state = np.copy(state)
        new_state[:, :-1] = np.roll(new_state[:, :-1], amount, axis=1)

        new_probs_array = np.copy(probs_array)
        new_probs_array[:, :, :-1] = np.roll(new_probs_array[:, :, :-1], amount, axis=2)

        return new_state, new_probs_array

    def start_play(self):

        game_manager = GameManager()

        step = 0
        episode_steps = []
        while True:
            step += 1
            if game_manager.winner != 0:
                sys.exit()

            if game_manager.player == 1:
                game_manager.event_handler.interactive = True
                game_manager.event_handler.check_events()
                game_manager.rendering_manager.render()
            else:
                game_manager.event_handler.interactive = False

                temperature = 0 if step < 30 else 0
                state = game_manager.get_state()
                player = game_manager.player
                turn = game_manager.turn

                if step == 1:
                    seen_states = []
                else:
                    seen_states = [step[0] for step in episode_steps]

                # Set the first_bug for the beginning of the episode
                self.gen_mcts.game_manager.first_bug_placed = game_manager.first_bug_placed
                probs_array = self.gen_mcts.get_policy_vector(state,
                                                              seen_states,
                                                              turn,
                                                              player,
                                                              temperature)
                for n_rot in range(6):
                    rotated_state, rotated_probs_array = self.rotate(state, probs_array, n_rot)
                    episode_steps.append([rotated_state, player, turn, rotated_probs_array, None])
                possibles_actions = np.argwhere(probs_array > 0)
                possibles_actions_probs = probs_array[possibles_actions[:, 0],
                                                      possibles_actions[:, 1],
                                                      possibles_actions[:, 2]]
                index = np.random.choice(len(possibles_actions), p=possibles_actions_probs)
                action = possibles_actions[index]
                game_manager.handle_connected_action(action)

            game_manager.rendering_manager.render()



    def generate_episode(self, winner_verbose=False):
        """
        Create an episode
        """
        episode_steps = []
        game_manager = GameManager(interactive=False,
                                   with_rendering=self.with_rendering,
                                   winner_verbose=winner_verbose)

        step = 0
        while True and step < 70:
            step += 1
            temperature = 1 if step < 30 else 0

            state = game_manager.get_state()

            player = game_manager.player
            turn = game_manager.turn

            if step == 1:
                seen_states = []
            else:
                seen_states = [step[0] for step in episode_steps]

            # Set the first_bug for the beginning of the episode
            self.gen_mcts.game_manager.first_bug_placed = game_manager.first_bug_placed
            probs_array = self.gen_mcts.get_policy_vector(state,
                                                          seen_states,
                                                          turn,
                                                          player,
                                                          temperature)


            # Manage every rotation
            for n_rot in range(6):
                rotated_state, rotated_probs_array = self.rotate(state, probs_array, n_rot)
                episode_steps.append([rotated_state, player, turn, rotated_probs_array, None])

            possibles_actions = np.argwhere(probs_array > 0)
            possibles_actions_probs = probs_array[possibles_actions[:, 0],
                                                  possibles_actions[:, 1],
                                                  possibles_actions[:, 2]]
            index = np.random.choice(len(possibles_actions), p=possibles_actions_probs)
            action = possibles_actions[index]


            state, player, turn = game_manager.handle_connected_action(action)

            reward = game_manager.get_end_value()

            if reward != 0:
                output = [(step[0], step[3], reward * (-1) ** (step[1] != player)) for step in episode_steps]
                return output
        # If too long, we try again
        retry_text = colored(f"Episode was too long, trying another one", "green")
        print(retry_text)
        self.gen_mcts.reset_tree()
        return self.generate_episode()

    def save_history(self, num_model):
        folder = "histories"
        filename = os.path.join(folder,
                                f"gen_game_by_{self.model_name}_{num_model}.examples")
        with open(filename, "wb+") as f:
            Pickler(f).dump(self.history)
        f.closed


    def train(self):

        n_steps = 100
        n_episodes = 3

        for i in range(1, n_steps + 1):
            # Generate episodes
            episodes_steps = deque([], maxlen=10000)

            for _ in tqdm(range(n_episodes), desc="Generating games"):
                self.gen_mcts.reset_tree()
                episodes_steps += self.generate_episode()

            # Save episodes in history
            self.history.append(episodes_steps)

            # We keep 10 times the amount of episodes per step
            while len(self.history) > 10:
                self.history.pop(0)

            self.save_history(i-1)

            length_text = colored(f"Training on {len(self.history)} episodes", "blue")
            print(length_text)

            steps_samples = []
            for episodes_steps in self.history:
                steps_samples.extend(episodes_steps)
            shuffle(steps_samples)

            self.net.save_ckpt(folder="models",
                                     filename=f"model_{self.model_name}_{i-1}.pth.tar")
            #self.compet_net.load_ckpt(folder="models",
            #                         filename="temp.pth.tar")
            self.net.train(steps_samples, n_epochs=1)
            self.net.save_ckpt(folder="models",
                                     filename=f"model_{self.model_name}_{i}.pth.tar")

    def load_history_and_net(self, old_model_name, num_model):
        folder = "histories"
        filename = os.path.join(folder,
                                f"gen_game_by_{old_model_name}_{num_model-1}.examples")
        with open(filename, "rb") as f:
            self.history = Unpickler(f).load()
        history_text = colored(f"History loaded with {len(self.history)} iterations",
                               "red")
        print(history_text)

        self.net.load_ckpt(filename=f"model_{old_model_name}_{num_model}.pth.tar")
        net_text = colored(f"Weights loaded", "yellow")
        print(net_text)











