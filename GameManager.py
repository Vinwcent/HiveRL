import pygame as pg

from gui.RenderingManager import RenderingManager
from gui.BoardSprite import BoardSprite
from gui.ButtonManager import ButtonManager

from EventHandler import EventHandler

from logic.LogicManager import LogicManager

screen_size = (1000, 800)

class GameManager():
    def __init__(self,
                 with_rendering=True,
                 interactive=True):
        self.with_rendering = with_rendering
        self.interactive = interactive

        self.bug_to_add = None
        self.turn = 1
        self.player = 1

        self.current_move_positions = None

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
                                              rendering_manager=self.rendering_manager)
        else:
            self.event_handler = EventHandler(game_manager=self)

        self.logic_manager = LogicManager(game_manager=self)

    def _init_gui(self):
        '''
        Init graphic interface if it is activated
        '''
        display = pg.display
        board = BoardSprite(screen_size)
        self.button_manager = ButtonManager(screen_size)
        self.rendering_manager = RenderingManager(display=display,
                                                  board=board,
                                                  button_manager=self.button_manager,
                                                  size=screen_size)

    ###
    ### Game functions used by event handler linking interaction, rendering and logic
    ###

    def start_add_piece(self, bug_name):
        '''
        Get the positions to add new Piece
        '''
        # If the turn is one then, the piece must be placed in the center directly
        if self.turn == 1:
            self.logic_manager.create_select_piece(bug_name=bug_name)
            self.logic_manager.move_select_piece(position=[14, 6, 0])
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




    def perform_board_action(self, logic_position):
        '''
        Move or get moving position on the board
        '''
        if logic_position in self.current_move_positions:
            self._move_piece(logic_position)
        else:
            self._get_moving_position(logic_position)


    def _get_moving_position(self, logic_position):
        '''
        Get the moving position of the piece under the given logic position
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
        self.logic_manager.move_select_piece(logic_position)
        self.current_move_positions = []
        self._update_board_rendering()
        self._next_turn()



    def _update_board_rendering(self):
        self.rendering_manager.update_board_pieces(self.logic_manager.pieces)

    ###
    ### Main
    ###

    def _next_turn(self):
        self.turn += 1
        self.player = 1 if self.player == 2 else 2

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
