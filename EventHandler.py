import pygame as pg
import sys

import pygame.mouse as mouse

# Import pygame constants
from pygame.locals import *

class EventHandler():

    def __init__(self,
                 game_manager,
                 rendering_manager=None,
                 interactive=True):
        self.game_manager = game_manager

        self.rendering_manager = rendering_manager
        self.button_manager = self.rendering_manager.button_manager
        self.board = self.rendering_manager.board

        self.interactive = interactive

        if self.interactive and rendering_manager is None:
            print("Game can't be interactive and headless")
            sys.exit()

    def check_events(self):
        events = pg.event.get()
        for event in events:
            if event.type == QUIT:
                sys.exit()
            elif event.type == MOUSEBUTTONDOWN:
                if (bug_name := self._get_button()) is not None:
                    self.game_manager.start_add_piece(bug_name=bug_name)
                elif (piece := self._get_piece()) is not None:
                    position = self.game_manager.get_piece_logic_position(piece)
                    self.game_manager.move_piece(position)
                    print(position)





    ###
    ### Board related events
    ###

    def _get_piece(self):
        '''
        Get the hypothetical piece hovered on the board
        '''
        mouse_position = self._get_relative_mouse_position(self.board.rect)
        for sprite_piece in self.board.sprite_pieces:
            if sprite_piece.rect.collidepoint(mouse_position):
                return sprite_piece
        return None



    ###
    ### Button Manager related events
    ###


    def _get_button(self):
        '''
        Get the hypothetical button hovered in the button manager
        '''
        mouse_position = self._get_relative_mouse_position(self.button_manager.rect)
        for button in self.button_manager.buttons:
            if button.rect.collidepoint(mouse_position):
                return button.bug_name
        return None


    ###
    ### Misc
    ###

    def _get_relative_mouse_position(self, rect):
        mouse_position = list(mouse.get_pos())
        mouse_position[0] -= rect[0]
        mouse_position[1] -= rect[1]
        return mouse_position

