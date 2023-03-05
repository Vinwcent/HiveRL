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


    def get_add_positions(self):
        nested_positions = self.board.get_empty_nested_positions()
        if len(nested_positions) == 0:
            return None
        return nested_positions


    def add_piece(self, position, bug_name):
        new_piece = Piece(position=position,
                          bug_name=bug_name,
                          player=self.game_manager.player)
        self.pieces.append(new_piece)
        self.update_board()


    def update_board(self):
        self.board.update(self.pieces)

