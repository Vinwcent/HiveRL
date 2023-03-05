import pygame as pg
import numpy as np

from logic.Board import Board
from logic.Piece import Piece


class LogicManager():

    def __init__(self,
                 game_manager):
        self.game_manager = game_manager
        self.board = Board()
        self.pieces = []

        self.selected_piece = None


    def get_nested_positions(self):
        nested_positions = self.board.get_empty_nested_positions()
        if len(nested_positions) == 0:
            return None
        return nested_positions


    def create_select_piece(self, bug_name):
        '''
        Create a new piece and select it (Not on board yet)
        '''
        self.selected_piece = Piece(position=[-1, -1, -1],
                                    bug_name=bug_name,
                                    player=self.game_manager.player)

    def move_select_piece(self, position):
        '''
        Move a piece to a given position, if the piece is not on the board,
        adds it to the board
        '''
        self.selected_piece.position = position
        if self.selected_piece not in self.pieces:
            self.pieces.append(self.selected_piece)
        self.update_board()


    def update_board(self):
        self.board.update(self.pieces)

