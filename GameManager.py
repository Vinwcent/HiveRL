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


        self.bug_to_place = None
        self.turn = 1
        self.player = 1

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

    def get_add_positions(self):
        '''
        Get the positions to add new Piece
        '''
        # If the turn is one then, the piece must be placed in the center
        if self.turn == 1:
            self.logic_manager.add_piece(position=[14, 6, 0],
                                         bug_name=self.bug_to_place)
            self.rendering_manager.update_board_pieces(self.logic_manager.pieces)
            self._next_turn()
            return


        if (add_positions := self.logic_manager.get_add_positions()) is not None:
            self.rendering_manager.highlight_board_positions(add_positions)


    ###
    ### Main
    ###

    def _next_turn(self):
        self.turn += 1
        self.player = 1 if self.player == 0 else 0

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
