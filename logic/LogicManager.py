import pygame as pg
import numpy as np

from logic.Board import Board
from logic.Piece import Piece


class LogicManager():
    '''
    The LogicManager makes the link between the pieces, the board and the GameManager.
    It modifies the board with the pieces array and makes the link between the GameManager
    and the logic of the board and the pieces
    '''

    def __init__(self,
                 game_manager):
        self.game_manager = game_manager
        self.board = Board()
        self.pieces = []

        self.selected_piece = None
        # A unique ID that increments when a piece is added
        self.ID = 0


    ###
    ### Hive Management
    ###
    # This section manage the trimming of positions to keep having a single hive
    # The idea is to take a piece, create an array of neighbors and repeat the process
    # on neighbors

    def _get_connected_IDs(self, piece):
        '''
        Get the array of pieces' IDs that are neighbors of piece but also of the piece that is over it
        '''
        connections = []
        neighbors = self.board.get_neighbor_position(piece.position)
        for other_piece in self.pieces:
            if other_piece.position[:2] in neighbors:
                connections.append(other_piece.ID)
            elif piece.position == [*other_piece.position, piece.position[2]+1]:
                connections.append(other_piece.ID)
        return connections

    def _is_hive_crucial(self, position):
        piece = self._get_piece_at_position(position)
        self.pieces.remove(piece)
        self.board.update(self.pieces)

        is_crucial_for_hive = not self._check_if_hive()

        self.pieces.append(piece)
        self.board.update(self.pieces)
        return is_crucial_for_hive

    def _check_if_hive(self):
        '''
        Check if the current board state has a unique hive
        '''
        check_count = 0
        connection_line = [self.pieces[check_count].ID]
        while check_count < len(connection_line):
            # One liner to get the corresponding piece
            piece_to_check = next(
                (piece
                 for piece in self.pieces
                 if piece.ID == connection_line[check_count]))

            connections = self._get_connected_IDs(piece_to_check)

            for ID in connections:
                if not ID in connection_line:
                    connection_line.append(ID)

            check_count += 1

        return len(self.pieces) == len(connection_line)

    ###
    ### Positions Management
    ###
    # This section is used to calculate an array of positions in various cases

    def get_nested_positions(self):
        nested_positions = self.board.get_empty_nested_positions()
        if len(nested_positions) == 0:
            return None
        return nested_positions


    def get_moving_positions(self, position):
        '''
        Get the moving positions of the piece located at position
        '''
        piece = self._get_piece_at_position(position)
        if piece.player != self.game_manager.player:
            return None

        # Instantly give up if the position is crucial to maintain
        # the hive
        if self._is_hive_crucial(position):
            return None


        positions = self.board.get_moving_positions(position)

        return positions


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


    def get_highest_z(self, position):
        return self.board.get_highest_z(position)


    def _is_exclusive(self, position, player):
        '''
        Function that checks if a position is exclusive to player
        '''
        neighbors = self.board.get_neighbor_position(position)
        for neighbor in neighbors:
            if (piece := self._get_piece_at_position([*neighbor, 0])) is not None:
                if piece.player != player:
                    return False
        return True

    ###
    ### Specific rules
    ###

    def is_bee_placed(self, player):
        for piece in self.pieces:
            if piece.player == player and piece.bug_name == "bee":
                return True
        return False

    def is_bee_selected(self):
        if self.selected_piece is not None:
            return self.selected_piece.bug_name == "bee"
        else:
            return False

    def bee_surrounded(self):
        '''
        Return the first bee piece that is surrounded by 6 pieces and None
        if there are not
        '''
        for piece in self.pieces:
            if piece.bug_name == "bee" and self.board.is_surrounded(piece.position):
                return piece
        return None


    def amount_of(self, bug_name, player):
        amount = 0
        for piece in self.pieces:
            if piece.bug_name == bug_name and piece.player == player:
                amount += 1
        return amount

    ###
    ### Piece Management
    ###
    # This section makes the connection between the action given by the GameManager and the
    # logic state of the game


    def create_select_piece(self, bug_name):
        '''
        Create a new piece and select it (Not on board yet)
        '''
        self.selected_piece = Piece(position=[-1, -1, -1],
                                    bug_name=bug_name,
                                    player=self.game_manager.player,
                                    ID = self.ID)

    def move_select_piece(self, position):
        '''
        Move a piece to a given position, if the piece is not on the board,
        adds it to the board
        '''
        self.selected_piece.position = position
        if self.selected_piece not in self.pieces:
            # If not inside, add it to the board and increment ID
            self.pieces.append(self.selected_piece)
            self.ID += 1
        self.update_board()
        self.selected_piece = None

    def select_piece(self, position):
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
            piece_at_position = next((piece for piece in self.pieces if piece.position == [*position[:2], z]), None)
            z -= 1
        return piece_at_position


    def update_board(self):
        self.board.update(self.pieces)

    ###
    ### RL Functions
    ###

    def get_board_array_and_pieces(self):
        return (self.board.board_array, self.pieces)

    def get_pieces_positions(self, player):
        positions = [piece.position
                     for piece in self.pieces
                     if piece.player == player]
        return positions


