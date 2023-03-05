import numpy as np

from Utilities import value_dic


class Board():
    '''
    The board is an abstract object composed of an array and various functions used to compute nested and sliding positions
    '''

    def __init__(self):
        self.board_array = np.zeros((43, 22, 5))

    def update(self, pieces):
        '''
        Update the board to the game state described by pieces
        '''
        self.board_array = np.zeros((43, 22, 5))
        for piece in pieces:
            piece_position = piece.position
            piece_value = value_dic[piece.bug_name]

            self.board_array[(*piece_position,)] = piece_value


    ###
    ### Neighbor functions
    ###

    def get_neighbor_position(self, position):
        i, j = position[:2]
        raw_neighbors = [[i+2, j],
                         [i-2, j],
                         [i+1, j+1],
                         [i+1, j-1],
                         [i-1, j+1],
                         [i-1, j-1]]
        neighbors = []
        for (pos_i, pos_j) in raw_neighbors:
            if self._check_if_inboard([pos_i, pos_j]):
                neighbors.append([pos_i, pos_j])
        return neighbors

    def get_neighbor_sliding(self, position):
        '''
        Function to get the neighbors of a position that are accessible with sliding
        '''
        pos_i, pos_j = position[:2]
        neighbors = self.get_neighbor_position(position)
        sliding = []
        for neighbor in neighbors:
            i, j = neighbor[:2]
            delta_i = i - pos_i
            delta_j = j - pos_j
            counter = 0
            if delta_i == 2:
                counter += 1 if self.board_array[pos_i+1, pos_j+1, 0] != 0 else 0
                counter += 1 if self.board_array[pos_i+1, pos_j-1, 0] != 0 else 0
            if delta_i == -2:
                counter += 1 if self.board_array[pos_i-1, pos_j+1, 0] != 0 else 0
                counter += 1 if self.board_array[pos_i-1, pos_j-1, 0] != 0 else 0
            if delta_i == 1:
                if delta_j == 1:
                    counter += 1 if self.board_array[pos_i-1, pos_j+1, 0] != 0 else 0
                    counter += 1 if self.board_array[pos_i+2, pos_j, 0] != 0 else 0
                if delta_j == -1:
                    counter += 1 if self.board_array[pos_i-1, pos_j-1, 0] != 0 else 0
                    counter += 1 if self.board_array[pos_i+2, pos_j, 0] != 0 else 0
            if delta_i == -1:
                if delta_j == 1:
                    counter += 1 if self.board_array[pos_i+1, pos_j+1, 0] != 0 else 0
                    counter += 1 if self.board_array[pos_i-2, pos_j, 0] != 0 else 0
                if delta_j == -1:
                    counter += 1 if self.board_array[pos_i+1, pos_j-1, 0] != 0 else 0
                    counter += 1 if self.board_array[pos_i-2, pos_j, 0] != 0 else 0

            if counter < 2:
                if self.board_array[i, j, 0] == 0:
                    sliding.append([*neighbor, 0])
        return sliding

    ###
    ### Nested functions
    ###

    def get_empty_nested_positions(self):
        '''
        Function to get the array of nested unoccupied positions
        '''
        nested = []
        for i in range(43):
            for j in range(22):
                if self.board_array[i, j, 0] == 0 and self._check_if_nested([i, j]):
                    nested.append([i, j, 0])

        return nested

    def _check_if_nested(self, position):
        position_array = self.get_neighbor_position(position)
        for pos in position_array:
            i, j = pos
            if (self.board_array[i, j, 0] != 0):
                return True
        return False

    ###
    ### Misc
    ###

    def _check_if_inboard(self, position):
        i, j = position[:2]
        if (i < 42) and (j < 21) and (i > 0) and (j > 0):
            return True
        return False




