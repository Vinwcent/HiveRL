import pygame as pg
import sys

from gui.RenderingManager import RenderingManager
from gui.BoardSprite import BoardSprite
from gui.ButtonManager import ButtonManager

from EventHandler import EventHandler

from logic.LogicManager import LogicManager
from Utilities import amounts_of_pieces



class GameManager():
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
        else:
            self.event_handler = EventHandler(game_manager=self,
                                             interactive=False)

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

            self.logic_manager.move_select_piece(position=[22, 11, 0])
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
        print("POSITION CLICK", logic_position)
        print("AVAILABLE POSITIONS", self.current_move_positions)
        if logic_position in self.current_move_positions:
            self._move_piece(logic_position)
        else:
            self._get_moving_position(logic_position)


    def _get_moving_position(self, logic_position):
        '''
        Get the moving position of the piece under the given logic position
        If rendering, the positions are highlighted
        '''
        if (move_positions := self.logic_manager.get_moving_positions(logic_position)) is not None:
            self.current_move_positions = move_positions

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
        print(logic_position)
        self.logic_manager.move_select_piece(logic_position)
        self.current_move_positions = []
        self._update_board_rendering()
        self._next_turn()



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
        # TODO
        return




    ###
    ### Game Management
    ###


    def _check_win(self):
        if (looser_piece := self.logic_manager.bee_surrounded()) is not None:
            winner = 1 if looser_piece.player == 2 else 2
            print(f"Winner is {winner}")
            sys.exit()

    def _next_turn(self):
        self._check_win()
        self.turn += 1
        self.player = 1 if self.player == 2 else 2
        print(f"Turn {self.turn}")

    def start_game(self):
        '''
        Start the game loop to manage events, logic and rendering
        '''

        self.button_manager.init_buttons()

        while True:
            self.event_handler.check_events()

            if self.with_rendering:
                self.rendering_manager.render()



if __name__ == "__main__":
    gameManager = GameManager()
    gameManager.start_game()
    print("DONE")
