import pygame as pg
import pygame.sprite as sprite

from gui.PieceSprite import PieceSprite

class BoardSprite(pg.sprite.Sprite):

    def __init__(self, screen_size):
        super(BoardSprite, self).__init__()
        self.surf = pg.Surface((int(screen_size[0]),
                                int(0.8*screen_size[1])))
        self.surf.fill((210, 130, 0))
        self.rect = self.surf.get_rect()
        # Center the board horizontally

        self.sprite_pieces = sprite.Group()


    def update_pieces(self, pieces):
        self.sprite_pieces = sprite.Group()
        for piece in pieces:
            pieceSprite = PieceSprite(background_int=1,
                                      bug_name=piece.bug_name)
            # pieceSprite.surf = pg.transform.scale_by(pieceSprite.surf,
            #                                       (1/2, 1/2))

            pieceSprite.rect[0] = piece.position[0] * 32 #/ (piece.position[0] % 2 + 1)
            pieceSprite.rect[1] = piece.position[1] * 46
            self.sprite_pieces.add(pieceSprite)

    def add_highlight_pieces(self, positions):
        for position in positions:
            pieceSprite = PieceSprite(background_int=0,
                                      bug_name=None)
            pieceSprite.rect[0] = position[0] * 32 #/ (position[0] % 2 + 1)
            pieceSprite.rect[1] = position[1] * 46
            self.sprite_pieces.add(pieceSprite)


    def _draw_pieces(self):
        for piece in self.sprite_pieces:
            self.surf.blit(piece.surf, piece.rect)

    def update(self):
        self._draw_pieces()

