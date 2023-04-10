import pygame as pg
import pygame.sprite as sprite
import sys

# Import pygame constants
from pygame.locals import *


background_color = 0, 0, 0

class RenderingManager():

    def __init__(self,
                 display,
                 board,
                 button_manager,
                 size,
                 no_transparencies=[]):
        self.display = display
        self.size = self.width, self.height = size
        self.board = board
        self.button_manager = button_manager
        self.no_transparencies = no_transparencies


        self.sprites = sprite.Group()

        self._init_screen()

    ##
    ## Sprite Management
    ##

    def _add_sprite(self, sprite):
        """
        Add sprite to the sprites to be rendered
        """
        self.sprites.add(sprite)

    def _draw_sprites(self):
        """
        Draw the sprite group to the screen
        """
        for sprite in self.sprites:
            self.screen.blit(sprite.surf, sprite.rect)

    def update_board_pieces(self, pieces):
        '''
        Update the sprite pieces group of the board with the pieces given by the logic
        '''
        self.board.update_pieces(pieces, no_transparencies=self.no_transparencies)

    def highlight_board_positions(self, positions):
        self.board.add_highlight_pieces(positions)


    ##
    ## Screen Management
    ##

    def _update_screen(self):
        """
        Update screen with newly drawn sprites
        """
        self.display.flip()

    def _init_screen(self):
        """
        Initialize the drawing screen according to size and fill it in black
        """
        self.screen = self.display.set_mode(size=self.size)
        self.screen.fill(background_color)

        self._init_screen_component()

    def _init_screen_component(self):
        """
        Add the button manager and the board
        """
        self._add_sprite(self.board)
        self._add_sprite(self.button_manager)

    ##
    ## Main Function
    ##

    def render(self):
        """
        Main function to render the current board sprite and button manager
        """

        self.board.update()
        self.button_manager.update()
        self._draw_sprites()
        self._update_screen()
