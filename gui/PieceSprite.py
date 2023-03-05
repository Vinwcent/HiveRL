import pygame as pg
import pygame.image as image

from pygame.locals import *

# Define the transparent color used to render images
transparent_color = (100, 100, 100)

class PieceSprite(pg.sprite.Sprite):

    def __init__(self,
                 background_int=0,
                 bug_name=None):
        super(PieceSprite, self).__init__()

        self.background_int = background_int
        self.bug_name = bug_name

        self._init_piece()


    def _init_piece(self):
        bg_img = image.load(f"art/piece_background_{self.background_int}.png")
        self.surf = bg_img.convert()
        self.surf.set_colorkey(transparent_color,
                               RLEACCEL)
        self.rect = self.surf.get_rect()

        if self.bug_name is not None:
            self._set_bug()

    def _set_bug(self):
        bug_img = image.load(f"art/{self.bug_name}.png")
        bug_surf = bug_img.convert()
        bug_surf.set_colorkey(transparent_color,
                              RLEACCEL)
        bug_rect = bug_surf.get_rect()


        self.surf.blit(bug_surf, bug_rect)


    def delete(self):
        self.kill()
