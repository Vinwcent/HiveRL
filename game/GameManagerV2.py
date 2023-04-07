import pygame as pg
import sys
import numpy as np

# Modify the path to work from main folder
import sys, os
sys.path.insert(0, os.getcwd())

from game.gui.RenderingManager import RenderingManager
from game.gui.BoardSprite import BoardSprite
from game.gui.ButtonManager import ButtonManager

from game.EventHandler import EventHandler

from game.logic.LogicManager import LogicManager
from game.Utilities import amounts_of_pieces, name_dic



class GameManagerV2():
    '''
    GameManager that enable rendering and calculations out of the box
    You can choose whether or not you enable rendering and interactivity,
    the screen_width of the game can also be modified
    '''
    def __init__(self,
                 with_rendering=True,
                 interactive=True,
                 screen_width=1400):
        self.with_rendering = with_rendering
        self.interactive = interactive
        self.screen_width = screen_width

        self.turn = 1
        self.player = 1

        self.current_move_positions = []

        # Bool to assess the end of the game (someone won)
        self.winner = 0



        self._init_game()

    ###
    ### Initialization
    ###

    def _init_game(self):
        '''
        Init the game and link the event handler to the renderer if rendering is activated
        '''
        if self.with_rendering:
            self._init_gui()
            self.event_handler = EventHandler(game_manager=self,
                                              rendering_manager=self.rendering_manager,
                                              interactive=self.interactive)

        self.logic_manager = LogicManager(game_manager=self)



    def _init_gui(self):
        '''
        Init graphic interface if it is activated
        '''
        display = pg.display
        screen_size = (self.screen_width, 0.9/1.3*self.screen_width)

        board = BoardSprite(screen_size)
        self.button_manager = ButtonManager(screen_size)
        self.rendering_manager = RenderingManager(display=display,
                                                  board=board,
                                                  button_manager=self.button_manager,
                                                  size=screen_size)
        self.button_manager.init_buttons()

    ###
    ### Game functions used by event handler linking interaction, rendering and logic
    ###

    ## Button Manager actions' functions

    def start_add_piece(self, bug_name):
        '''
        Prepare the logic to add a piece and show the positions to add it
        '''
        # Clean the movements showed
        self._update_board_rendering()

        # If the turn is one then, the piece must be placed in the center directly
        if self.turn == 1:
            self.logic_manager.create_select_piece(bug_name=bug_name)

            self.logic_manager.move_select_piece(position=[43, 22, 0])
            self._update_board_rendering()
            self._next_turn()
            return
        elif self.turn == 2:
            self.logic_manager.create_select_piece(bug_name=bug_name)
            add_positions = self.logic_manager.get_nested_positions()
        else:
            self.logic_manager.create_select_piece(bug_name=bug_name)
            add_positions = self.logic_manager.get_exclusive_nested_positions(self.player)

        if add_positions is not None:
            self.current_move_positions = add_positions

            # Rendering management
            if self.with_rendering:
                self.rendering_manager.highlight_board_positions(add_positions)



    ## Board actions' functions

    def perform_board_action(self, logic_position):
        '''
        Move or get moving position on the board
        '''
        self._update_board_rendering()
        if logic_position in self.current_move_positions:
            self._move_piece(logic_position)
            self._next_turn()
        else:
            self._get_moving_position(logic_position)


    def _get_moving_position(self, logic_position):
        '''
        Get the moving position of the piece under the given logic position
        If rendering, the positions are highlighted
        '''
        if (move_positions := self.logic_manager.get_moving_positions(logic_position)) is not None:
            self.current_move_positions = move_positions
            self.logic_manager.select_piece(logic_position)

            # Rendering Management
            if self.with_rendering:
                self.rendering_manager.highlight_board_positions(move_positions)
        else:
            if self.with_rendering:
                self._update_board_rendering()


    def _move_piece(self, logic_position):
        '''
        Move the current selected piece to the logic_position
        '''
        self.logic_manager.move_select_piece(logic_position)
        self.current_move_positions = []
        if self.with_rendering:
            self._update_board_rendering()



    def _update_board_rendering(self):
        self.rendering_manager.update_board_pieces(self.logic_manager.pieces)

    ###
    ### Specific rules
    ###

    def is_bee_placed(self):
        return self.logic_manager.is_bee_placed(self.player)

    def is_bee_selected(self):
        return self.logic_manager.is_bee_selected()

    def can_add(self, bug_name):
        '''
        Check if the current player can add bug_name on the board
        '''
        current_amount = self.logic_manager.amount_of(bug_name,
                                                      self.player)
        return amounts_of_pieces[bug_name] > current_amount

    def no_available_move(self):
        '''
        Checks if the current player can play
        '''
        action_space = self.get_legal_action_space()
        return len(action_space) == 0




    ###
    ### Game Management
    ###


    def _check_win(self):
        if (looser_piece := self.logic_manager.bee_surrounded()) is not None:
            self.winner = 1 if looser_piece.player == 2 else 2
            print(f"Winner is player {self.winner}")

    def _next_turn(self):
        self._check_win()
        self.turn += 1
        self.player = 1 if self.player == 2 else 2
        #print(f"Turn {self.turn}")

        self.logic_manager.try_normalize_board(self.player)
        if self.with_rendering:
            self._update_board_rendering()

        if self.no_available_move():
            self._next_turn()


    ###
    ### Game start
    ###

    def start_full_interactive(self):
        '''
        Start the game loop that manage the game for two human
        players (on the same computer)
        '''
        self.event_handler.interactive = True
        while True:

            if self.winner != 0:
                sys.exit()

            self.event_handler.check_events()

            if self.with_rendering:
                self.rendering_manager.render()


    ###
    ### RL Functions
    ###

    def get_amount_blocking_bee(self, player):
        '''
        Get the amount of pieces around the bee of the player's enemy
        '''
        amount_enemy = self.logic_manager.amount_blocking_bee(player)
        return amount_enemy

    def update_render(self):
        self.rendering_manager.render()

    def get_state_info(self):
        board_array, pieces = self.logic_manager.get_board_array_and_pieces()

        current_player_pieces = np.zeros((88, 45, 5))
        current_player_pieces_positions = np.array([piece.position
                                           for piece in pieces
                                           if piece.player == self.player])
        for position in current_player_pieces_positions:
            current_player_pieces[(*position,)] = 1

        # We compute the state which is the board piece and the pieces that
        # belong to the player
        state = np.concatenate([board_array, current_player_pieces], axis=2)



        # Compute played pieces per player for info
        player_1_pieces = {"bee": 0,
                           "ant": 0,
                           "spider": 0,
                           "beetle": 0,
                           "grasshopper": 0}
        player_2_pieces = {"bee": 0,
                           "ant": 0,
                           "spider": 0,
                           "beetle": 0,
                           "grasshopper": 0}
        for piece in pieces:
            if piece.player == 1:
                player_1_pieces[piece.bug_name] += 1
            else:
                player_2_pieces[piece.bug_name] += 1
        info = [player_1_pieces, player_2_pieces]


        return state, info

    def handle_RL_action(self, action, reward_mode):
        '''
        Perform RL Action without checking if they are legal and return the
        state of the current agent post action
        '''
        start_position = action[0]
        end_position = action[1]
        if -1 in start_position:
            piece_value = start_position[0]
            bug_name = name_dic[piece_value]
            self.logic_manager.create_select_piece(bug_name)
            self._move_piece(end_position)
        else:
            self.logic_manager.select_piece(start_position)
            self._move_piece(end_position)

        # Can be the same player here
        self._next_turn()
        next_state, info = self.get_state_info()

        if self.with_rendering:
            self.rendering_manager.render()

        return next_state, info

    def get_add_actions(self):
        '''
        Function to calculate the actions that add a bug for the RL algorithm
        '''
        if self.turn == 1:
            add_positions = [[[i, -1, -1], [43, 22, 0]]
                             for i in range(1, 6)]
            return add_positions

        # We check which bug are still available
        start_positions = [[i, -1, -1] for i in range(1, 6)
                          if self.can_add(name_dic[i])]

        # Add action is special at turn 2
        if self.turn == 2:
            end_positions = self.logic_manager.get_nested_positions()
        else:
            end_positions = self.logic_manager.get_exclusive_nested_positions(self.player)

        # If bee is not placed, then only the bee can be placed
        if (self.turn == 5 or self.turn == 6) and not self.is_bee_placed():
            start_positions = [[1, -1, -1]]


        add_positions = []
        if end_positions is None:
            return add_positions

        for start_pos in start_positions:
            for end_pos in end_positions:
                add_positions.append([start_pos, end_pos])

        return add_positions



    def get_legal_action_space(self):
        legal_action_space = []

        if self.turn == 1 or self.turn == 2:
            return self.get_add_actions()

        # If bee not placed, return the only add action with bees
        if (self.turn == 5 or self.turn == 6) and not self.is_bee_placed():
            return self.get_add_actions()

        add_actions = self.get_add_actions()
        move_actions = []
        start_moving_positions = self.logic_manager.get_pieces_positions(self.player)
        for start_pos in start_moving_positions:
            if (end_positions := self.logic_manager.get_moving_positions(start_pos)) is not None:
                for end_pos in end_positions:
                    move_actions.append([start_pos, end_pos])
        return add_actions + move_actions




if __name__ == "__main__":
    gameManager = GameManager()
    gameManager.start_full_interactive()
    print("DONE")
