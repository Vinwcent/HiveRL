import pygame as pg
import pygame.image as image
import pygame.transform as transform

from pygame.locals import *

# Define the transparent color used to render images
transparent_color = (100, 100, 100)

class PieceSprite(pg.sprite.Sprite):

    def __init__(self,
                 background_int=0,
                 bug_name=None,
                 scale=[1, 1]):
        super(PieceSprite, self).__init__()

        self.background_int = background_int
        self.bug_name = bug_name
        self.z = 0
        self.scale = scale

        self._init_piece()


    def set_transparency(self, transparency):
        '''
        Change the transparency of the piece on a scale from 0 to 255
        '''
        self.surf.set_alpha(transparency)

    def set_scale(self, scale):
        '''
        Modify the scale of the sprite accordingly
        '''
        self.surf = pg.transform.scale_by(self.surf, scale)

    def _init_piece(self):
        bg_img = image.load(f"art/piece_background_{self.background_int}.png")
        self.surf = bg_img.convert()
        self.surf = transform.scale_by(self.surf, self.scale)
        self.surf.set_colorkey(transparent_color,
                               RLEACCEL)
        self.rect = self.surf.get_rect()

        if self.bug_name is not None:
            self._set_bug()

    def _set_bug(self):
        bug_img = image.load(f"art/{self.bug_name}.png")
        bug_surf = bug_img.convert()
        bug_surf = transform.scale_by(bug_surf, self.scale)
        bug_surf.set_colorkey(transparent_color,
                              RLEACCEL)
        bug_rect = bug_surf.get_rect()


        self.surf.blit(bug_surf, bug_rect)

    def rect_position(self):
        return list(self.rect[0:2])


    def delete(self):
        self.kill()
