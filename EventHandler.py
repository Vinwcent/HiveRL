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
            # Interactive  events
            elif event.type == MOUSEBUTTONDOWN:
                if (bug_name := self._get_button_bug_name()) is not None:
                    self.game_manager.start_add_piece(bug_name=bug_name)
                elif (logic_position := self._get_logic_position_from_mouse()) is not None:
                    self.game_manager.perform_board_action(logic_position)





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


    def _get_piece_logic_position(self, sprite_piece):
        '''
        Get the logic position of a sprite piece
        '''
        rect_x, rect_y = sprite_piece.rect_position()
        i = rect_x // 32
        j = rect_y // 46
        return [i, j, 0]

    def _get_logic_position_from_mouse(self):
        '''
        Get logic position from the sprite hovered by the mouse if it exists
        '''
        if (piece := self._get_piece()) is not None:
            logic_position = self._get_piece_logic_position(piece)
            return logic_position
        return None


    ###
    ### Button Manager related events
    ###


    def _get_button_bug_name(self):
        '''
        Get the bug name of the hypothetical button hovered in the button manager
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

