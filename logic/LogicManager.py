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


    ###
    ### Positions Management
    ###

    def get_nested_positions(self):
        nested_positions = self.board.get_empty_nested_positions()
        if len(nested_positions) == 0:
            return None
        return nested_positions

    def get_exclusive_nested_positions(self, player):
        '''
        Get nested_positions that are connected only to player's pieces
        Return None if there None available
        '''
        if (nested_positions := self.board.get_empty_nested_positions()) is not None:
            exclusive_nested = [position
                                for position in nested_positions
                                if self._is_exclusive(position, player)]

        return exclusive_nested if len(exclusive_nested) > 0 else None

    def get_moving_positions(self, position):
        '''
        Get the moving positions of the piece located at position
        '''
        piece = self._get_piece_at_position(position)
        if piece.player != self.game_manager.player:
            return None
        self._select_piece(position)

        return self.board.get_neighbor_sliding(position)


    def _is_exclusive(self, position, player):
        '''
        Function that checks if a position is exclusive to player
        '''
        neighbors = self.board.get_neighbor_position(position)
        for piece in self.pieces:
            if piece.position[:2] in neighbors and piece.player != player:
                return False
        return True



    ###
    ### Piece Management
    ###

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

    def _select_piece(self, position):
        # Classic one-liner to get the first piece matching the position condition
        if (possible_piece := self._get_piece_at_position(position)) is not None:
            self.selected_piece = possible_piece


    def _get_piece_at_position(self, position):
        '''
        Get the piece with the highest z at a given location
        '''
        piece_at_position = None
        z = 4
        while piece_at_position is None and z >= 0:
            piece_at_position = next((piece for piece in self.pieces if piece.position == [*position[:2], 0]), None)
            z -= 1
        return piece_at_position


    def update_board(self):
        self.board.update(self.pieces)

