import pygame as pg
import pygame.sprite as sprite
import pygame.transform as transform

from game.gui.PieceSprite import PieceSprite

class BoardSprite(pg.sprite.Sprite):

    def __init__(self, screen_size):
        super(BoardSprite, self).__init__()
        board_size = (int(0.9*screen_size[0]),
                      int(screen_size[1]))

        self.surf = pg.Surface(board_size)
        self.surf.fill((210, 130, 0))
        # We want a max of 22 pieces on the board
        self.piece_x_scale = (board_size[0]/44) / 64
        self.piece_y_scale = (board_size[1]/32) / 64
        self.rect = self.surf.get_rect()
        # Center the board horizontally

        self.sprite_pieces = []


    def update_pieces(self, pieces):
        self.sprite_pieces = None
        self.sprite_pieces = []
        for piece in pieces:
            piece_sprite = PieceSprite(background_int=piece.player,
                                      bug_name=piece.bug_name,
                                      scale=[self.piece_x_scale, self.piece_y_scale])

            piece_sprite.rect[0] = piece.position[0] * 32 * self.piece_x_scale
            piece_sprite.rect[1] = piece.position[1] * 46 * self.piece_y_scale
            piece_sprite.z = piece.position[2]

            # Beetle modification
            piece_sprite.set_scale(1 - 0.1*piece_sprite.z)

            self.sprite_pieces.append(piece_sprite)

    def add_highlight_pieces(self, positions):
        for position in positions:
            piece_sprite = PieceSprite(background_int=0,
                                      bug_name=None,
                                      scale=[self.piece_x_scale, self.piece_y_scale])

            piece_sprite.set_transparency(150)
            # We calculate and center since the surf is referenced by top left
            piece_sprite.rect[0] = position[0] * 32 * self.piece_x_scale
            piece_sprite.rect[1] = position[1] * 46 * self.piece_y_scale
            piece_sprite.z = position[2]
            self.sprite_pieces.append(piece_sprite)


    def _draw_pieces(self):
        self.surf.fill((210, 130, 0))
        self.sprite_pieces.sort(key=lambda x: x.z, reverse=False)
        for piece in self.sprite_pieces:
            self.surf.blit(piece.surf, piece.rect)

    def update(self):
        self._draw_pieces()

