import pygame as pg
import numpy as np
import time

from game.logic.Board import Board
from game.logic.Piece import Piece

from game.Utilities import amounts_of_pieces, name_dic


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

    def get_connected_IDs(self, piece):
        '''
        Get the array of pieces' IDs that are neighbors of piece but also of the piece that is over
        The 6 first values follow the get_neighbor order and the last one is over
        '''
        connections = [0, 0, 0, 0, 0, 0, 0]
        neighbors = self.board.get_neighbor_position(piece.position)
        for other_piece in self.pieces:
            index = -1
            if other_piece.position[:2] in neighbors and other_piece.position[2] == piece.position[2]:
                index = neighbors.index(other_piece.position[:2])
            # Over
            elif other_piece.position == [*piece.position[:2], piece.position[2]+1]:
                index = 6


            if index != -1:
                connections[index] = other_piece.ID

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

            connections = np.array(self.get_connected_IDs(piece_to_check))
            connections = connections[connections != 0]

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

    def amount_blocking_bee(self, player):
        '''
        Return the amount of pieces around the enemy bee and the amount of pieces around the player bee
        '''
        enemy_bee = None
        ally_bee = None
        for piece in self.pieces:
            if piece.bug_name == "bee":
                if piece.player == player:
                    ally_bee = piece
                else:
                    enemy_bee = piece
        amount_enemy = 0
        amount_ally = 0

        if ally_bee is not None:
            amount_ally = self.board.amount_surrounding(ally_bee.position)

        if enemy_bee is not None:
            amount_enemy = self.board.amount_surrounding(enemy_bee.position)

        return amount_enemy


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

    def affect_ID(self, bug_name, player):
        """
        Gives the unique ID of the piece.
        Bee -> 1
        Ant -> 2,3,4
        Grasshopper -> 5, 6, 7
        spider -> 8, 9
        Beetle -> 10, 11
        Negative value for player 2
        """
        start_value_dic = {"bee": 1,
                           "ant": 2,
                           "grasshopper": 5,
                           "spider": 8,
                           "beetle": 10}
        amount = self.amount_of(bug_name, player)
        player_offset = (player - 1) * 11
        ID = player_offset + start_value_dic[bug_name] + amount
        return ID




    def create_select_piece(self, bug_name):
        '''
        Create a new piece and select it (Not on board yet)
        '''
        player = self.game_manager.player
        self.selected_piece = Piece(position=[-1, -1, -1],
                                    bug_name=bug_name,
                                    player=player,
                                    ID = self.affect_ID(bug_name, player))

    def move_select_piece(self, position):
        '''
        Move a piece to a given position, if the piece is not on the board,
        adds it to the board
        '''
        self.selected_piece.position = position
        if self.selected_piece not in self.pieces:
            # If not inside, add it to the board and set ID
            self.pieces.append(self.selected_piece)
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

    ###
    ### RL Functions
    ###

    def update_board(self):
        self.board.update(self.pieces)

    def _apply_connection_index(self, position, connection_index):
        '''
        Apply the right offset to position with connection index
        '''
        offset_position = position.copy()
        if connection_index == 0:
            offset_position[0] += 2
        elif connection_index == 1:
            offset_position[0] += 1
            offset_position[1] += 1
        elif connection_index == 2:
            offset_position[0] -= 1
            offset_position[1] += 1
        elif connection_index == 3:
            offset_position[0] -= 2
        elif connection_index == 4:
            offset_position[0] -= 1
            offset_position[1] -= 1
        elif connection_index == 5:
            offset_position[0] += 1
            offset_position[1] -= 1
        elif connection_index == 6:
            offset_position[2] += 1
        return offset_position

    def _get_bug_name_from_ID(self, ID_without_offset):
        '''
        Return bug name from the ID, only works with ID in [1, 11]
        '''
        if ID_without_offset > 9:
            bug_name = "beetle"
        elif ID_without_offset > 7:
            bug_name = "spider"
        elif ID_without_offset > 4:
            bug_name = "grasshopper"
        elif ID_without_offset > 1:
            bug_name = "ant"
        else:
            bug_name = "bee"
        return bug_name


    def _create_piece_from_connection(self, neighbor_ID, connection_index, ID):
        neighbor_position = next((piece.position for piece in self.pieces if piece.ID == neighbor_ID), None)
        position = self._apply_connection_index(neighbor_position, connection_index)
        player = 1 if ID < 12 else 2
        ID_without_offset = ID - 11 * (player - 1)
        start_value_dic = {"bee": 1,
                           "ant": 2,
                           "grasshopper": 5,
                           "spider": 8,
                           "beetle": 10}
        bug_name = self._get_bug_name_from_ID(ID_without_offset)
        new_piece = Piece(position, bug_name, player, ID)
        return new_piece


    def load_connections_array(self, connection_array, current_ID=None):
        """
        Convert recursively the connection state array to a piece array
        """
        if current_ID is None:
            current_ID = 1
            self.pieces = [Piece([43, 22, 0], "bee", 1, current_ID)]


        connection_line = np.array(connection_array[current_ID-1], dtype=int)
        for index, ID in enumerate(connection_line):
            if ID > 0 and ID not in [piece.ID for piece in self.pieces]:
                new_piece = self._create_piece_from_connection(current_ID, index, ID)
                self.pieces.append(new_piece)
                self.load_connections_array(connection_array, ID)
        self.board.update(self.pieces)

    def get_pieces_positions(self, player):
        positions = [piece.position
                     for piece in self.pieces
                     if piece.player == player]
        return positions

    ###
    ### Action Space (Board Design)
    ###

    def can_add(self, bug_name, player):
        '''
        Check if the current player can add bug_name on the board
        '''
        current_amount = self.amount_of(bug_name,
                                        player)
        return amounts_of_pieces[bug_name] > current_amount

    def _get_add_actions(self, player, turn):
        '''
        Get the legal add actions
        '''
        if turn == 1:
            add_positions = [[[i, -1, -1], [43, 22, 0]]
                             for i in range(1, 6)]
            return add_positions
        # We check which bug are still available
        start_positions = [[i, -1, -1] for i in range(1, 6)
                          if self.can_add(name_dic[i], player)]
        # Add action is special at turn 2
        if turn == 2:
            end_positions = self.get_nested_positions()
        else:
            end_positions = self.get_exclusive_nested_positions(player)
        # If bee is not placed, then only the bee can be placed
        if (turn == 5 or turn == 6) and not self.is_bee_placed(player):
            start_positions = [[1, -1, -1]]

        add_positions = []
        if end_positions is None:
            return add_positions

        for start_pos in start_positions:
            for end_pos in end_positions:
                add_positions.append([start_pos, end_pos])

        return add_positions



    def get_legal_action_space(self, player, turn):
        '''
        Get the legal action space in [start_position, end_position] format
        '''
        legal_action_space = []
        add_actions = self._get_add_actions(player, turn)
        if (turn == 1 or
            turn == 2 or
            ((turn == 5 or turn == 6) and not self.is_bee_placed(player))):
            return add_actions

        move_actions = []
        start_moving_positions = self.get_pieces_positions(player)
        for start_pos in start_moving_positions:
            if (end_positions := self.get_moving_positions(start_pos)) is not None:
                for end_pos in end_positions:
                    move_actions.append([start_pos, end_pos])
        return add_actions + move_actions

    ###
    ### Action Space (Connected Design)
    ###
    def get_piece(self, position):
        '''
        Return the the piece at position if it exists, else None
        '''
        hypothetic_piece = next((piece
                                 for piece in self.pieces
                                 if piece.position == position), None)
        return hypothetic_piece

    def get_connected_state(self):
        '''
        Get the state according to player 1
        '''
        connections_array = np.zeros((22, 7))
        for piece in self.pieces:
            ID = piece.ID
            connections = self.get_connected_IDs(piece)
            connections_array[ID-1] = connections
        return connections_array

    def revert_connected_array(self, connections_array):
        """
        Revert the player side of the connected array
        """
        connections_array = np.array(connections_array)
        save = np.copy(connections_array)

        connections_array = np.where((connections_array < 12) & (connections_array > 0), connections_array + 11, connections_array - 11)
        connections_array = np.where(connections_array == -11, 0, connections_array)
        connections_array = np.vstack((connections_array[11:, :],
                                       connections_array[:11, :]))

        return connections_array

    def reload_board_with_connections(self):
        '''
        Reload the board with the connections array. Mainly used to center
        the board
        '''
        connections_array = self.get_connected_state()
        self.load_connections_array(connections_array)


    def _get_ID_index(self, position):
        '''
        Function which returns an array of IDs and index which represents the connection index
        of the position according to the ID
        '''
        ID = []
        connections_index = []
        # Neighbors
        neighbors = self.board.get_neighbor_position(position)
        for neighbor in neighbors:
            if (piece := self.get_piece([*neighbor, position[2]])) is not None:
                if piece.position[0] - position[0] == 2:
                    connection_index = 3
                elif piece.position[0] - position[0] == -2:
                    connection_index = 0
                elif piece.position[0] - position[0] == 1 and piece.position[1] - position[1] == 1:
                    connection_index = 4
                elif piece.position[0] - position[0] == 1 and piece.position[1] - position[1] == -1:
                    connection_index = 2
                elif piece.position[0] - position[0] == -1 and piece.position[1] - position[1] == 1:
                    connection_index = 5
                elif piece.position[0] - position[0] == -1 and piece.position[1] - position[1] == -1:
                    connection_index = 1
                ID.append(piece.ID)
                connections_index.append(connection_index)
        # Below
        if (piece := self.get_piece([*position[:2], position[2] - 1])) is not None:
            ID.append(piece.ID)
            connections_index.append(6)

        return ID, connections_index

    def get_legal_connected_action_space(self, player, turn):
        if turn == 1:
            return np.ones((11, 22, 7))
        mask = np.zeros((11, 22, 7))
        board_action_space = self.get_legal_action_space(player, turn)
        for board_action in board_action_space:
            # Move actions
            if (piece := self.get_piece(board_action[0])) is not None:
                ID = piece.ID
            # Add actions
            elif board_action[0][1] == -1:
                 bug_name = name_dic[board_action[0][0]]
                 ID = self.affect_ID(bug_name, player)
            ID_array, connections_index = self._get_ID_index(board_action[1])

            for index in range(len(ID_array)):
                # If the piece move, she won't be connected to herself
                if ID == ID_array[index]:
                    continue

                # manage ID difference due to player
                other_ID = ID_array[index]
                if player != 1:
                    other_ID = other_ID + 11 if other_ID < 12 else other_ID - 11
                    ID = ID - 11 if ID > 11 else ID

                mask[ID - 1, other_ID - 1, connections_index[index]] = 1
        return mask







