import pygame as pg
import sys
import numpy as np
import time

# Modify the path to work from main folder
import sys, os
sys.path.insert(0, os.getcwd())

from game.gui.RenderingManager import RenderingManager
from game.gui.BoardSprite import BoardSprite
from game.gui.ButtonManager import ButtonManager

from game.EventHandler import EventHandler

from game.logic.LogicManager import LogicManager
from game.Utilities import amounts_of_pieces, name_dic, value_dic



class GameManager():
    '''
    GameManager that enable rendering and calculations out of the box
    You can choose whether or not you enable rendering and interactivity,
    the screen_width of the game can also be modified
    '''
    def __init__(self,
                 with_rendering=True,
                 interactive=True,
                 screen_width=1400,
                 winner_verbose=False):
        self.with_rendering = with_rendering
        self.interactive = interactive
        self.screen_width = screen_width

        self.turn = 1
        self.player = 1

        self.current_move_positions = []

        # Bool to assess the end of the game (someone won)
        self.winner = 0
        self.winner_verbose = winner_verbose



        self._init_game()

        self.possible_connected_actions = [[x, y, z]
                                           for x in range(11)
                                           for y in range(22)
                                           for z in range(7)]

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
        return self.logic_manager.can_add(bug_name, self.player)

    def no_available_move(self):
        '''
        Checks if the current player can play
        '''
        action_space = self.logic_manager.get_legal_action_space(self.player, self.turn)
        return len(action_space) == 0




    ###
    ### Game Management
    ###


    def _check_win(self):
        if (looser_piece := self.logic_manager.bee_surrounded()) is not None:
            self.winner = 1 if looser_piece.player == 2 else 2
            if self.winner_verbose:
                print(f"Winner is player {self.winner}")

    def _next_turn(self):
        self._check_win()
        self.turn += 1
        self.player = 1 if self.player == 2 else 2
        #print(f"Turn {self.turn}")

        self.logic_manager.reload_board_with_connections()

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

    def update_render(self):
        self.rendering_manager.render()



    ###
    ### Board Action
    ###

    def handle_board_action(self, action):
        '''
        Perform a board based action
        '''
        start_position = action[0]
        end_position = action[1]
        if -1 in start_position:
            bug_name = name_dic[start_position[0]]
            self.logic_manager.create_select_piece(bug_name)
        else:
            self.logic_manager.select_piece(start_position)

        self._move_piece(end_position)
        self._next_turn()
        if self.with_rendering:
            self.rendering_manager.render()


    def get_legal_action_space(self):
        return self.logic_manager.get_legal_action_space(self.player, self.turn)



    ###
    ### Connected Actions
    ###

    def get_end_value(self):
        if self.winner == 0:
            return 0
        else:
            return 1 if self.winner == self.player else -1

    def get_state(self):
        # Turn 1 and 2 are the same since there's no connection
        # We need to tell which pieces has been played on turn 1
        if self.turn == 2:
            piece = self.logic_manager.pieces[0]
            return np.ones((22, 7)) * value_dic[piece.bug_name]

        connected_state = self.logic_manager.get_connected_state()
        if self.player == 2:
            connected_state = self.logic_manager.revert_connected_array(connected_state)

        return connected_state

    def load_state(self, c_state, turn, player):
        '''
        Load a connected state and set the turn
        '''
        self.player = player
        self.turn = turn
        self.winner = 0
        if player == 2:
            c_state = self.logic_manager.revert_connected_array(c_state)
        self.logic_manager.load_connections_array(c_state)

    def get_legal_connected_action_space(self):
        return self.logic_manager.get_legal_connected_action_space(self.player, self.turn)

    def handle_connected_action(self, action_index):
        real_piece_ID = action_index[0] + 1
        if self.player != 1:
            real_piece_ID += 11

        start_pos = next((piece.position
                          for piece in self.logic_manager.pieces
                          if piece.ID == real_piece_ID), None)

        connected_ID = action_index[1] + 1
        if self.player != 1:
            connected_ID = connected_ID + 11 if connected_ID < 12 else connected_ID - 11
        #print("Real piece ID ", real_piece_ID)
        #print("Action asked ", action_index)
        #print("Player ", self.player)
        #print("connected ID ", connected_ID)
        #print("IDs ", [piece.ID for piece in self.logic_manager.pieces])

        connected_pos = next((piece.position
                          for piece in self.logic_manager.pieces
                          if piece.ID == connected_ID), None)

        # Handle add_actions
        if start_pos is None:
            bug_name = self.logic_manager._get_bug_name_from_ID(action_index[0] + 1)
            bug_index = value_dic[bug_name]
            start_pos = [bug_index, -1, -1]
        # Handle turn 1
        if self.turn == 1:
            end_pos = [43, 22, 0]
        else:
            end_pos = self.logic_manager._apply_connection_index(connected_pos, action_index[2])

        board_action = [start_pos, end_pos]
        self.handle_board_action(board_action)

        resulting_state = self.get_state()
        resulting_player = self.player
        resulting_turn = self.turn

        return resulting_state, resulting_player, resulting_turn




if __name__ == "__main__":
    gameManager = GameManager()
    gameManager.start_full_interactive()
    print("DONE")
