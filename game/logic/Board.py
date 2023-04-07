import numpy as np

from game.Utilities import value_dic
from game.Utilities import name_dic


class Board():
    '''
    The board is an abstract object composed of an array and various functions used to compute positions.

    The board doesn't manage exclusive positions and trimmed positions.
    '''

    def __init__(self):
        self.board_array = np.zeros((88, 45, 5))

    def update(self, pieces):
        '''
        Update the board to the game state described by pieces
        '''
        self.board_array = np.zeros((88, 45, 5))
        for piece in pieces:
            piece_position = piece.position
            piece_value = value_dic[piece.bug_name]

            self.board_array[(*piece_position,)] = piece_value


    ###
    ### Neighbor functions
    ###
    # This section manage the calculation of neighbors of positions

    def get_neighbor_position(self, position):
        '''
        Particular function that get the x, y position of neighbors in a array looking circularly
        '''
        i, j = position[:2]
        raw_neighbors = [[i+2, j],
                         [i+1, j+1],
                         [i-1, j+1],
                         [i-2, j],
                         [i-1, j-1],
                         [i+1, j-1]]
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
        z = position[2]
        neighbors = self.get_neighbor_position(position)
        sliding = []
        for neighbor in neighbors:
            i, j = neighbor[:2]
            delta_i = i - pos_i
            delta_j = j - pos_j
            counter = 0
            if delta_i == 2:
                counter += 1 if self.board_array[pos_i+1, pos_j+1, z] != 0 else 0
                counter += 1 if self.board_array[pos_i+1, pos_j-1, z] != 0 else 0
            if delta_i == -2:
                counter += 1 if self.board_array[pos_i-1, pos_j+1, z] != 0 else 0
                counter += 1 if self.board_array[pos_i-1, pos_j-1, z] != 0 else 0
            if delta_i == 1:
                if delta_j == 1:
                    counter += 1 if self.board_array[pos_i-1, pos_j+1, z] != 0 else 0
                    counter += 1 if self.board_array[pos_i+2, pos_j, z] != 0 else 0
                if delta_j == -1:
                    counter += 1 if self.board_array[pos_i-1, pos_j-1, z] != 0 else 0
                    counter += 1 if self.board_array[pos_i+2, pos_j, z] != 0 else 0
            if delta_i == -1:
                if delta_j == 1:
                    counter += 1 if self.board_array[pos_i+1, pos_j+1, z] != 0 else 0
                    counter += 1 if self.board_array[pos_i-2, pos_j, z] != 0 else 0
                if delta_j == -1:
                    counter += 1 if self.board_array[pos_i+1, pos_j-1, z] != 0 else 0
                    counter += 1 if self.board_array[pos_i-2, pos_j, z] != 0 else 0

            if counter < 2:
                if self.board_array[i, j, z] == 0 and self._has_occupied_neighbor([*neighbor, 0], position):
                    # Check if the place is empty and has neighbors
                    sliding.append([i, j, z])
        return sliding

    def _has_occupied_neighbor(self, position_to_check, position):
        '''
        Tell if a given position to check has an occupied neighbor other than position
        '''
        neighbors = self.get_neighbor_position(position_to_check)
        for neighbor in neighbors:
            if self.board_array[(*neighbor, 0)] != 0 and [*neighbor, 0] != position:
                return True
        return False

    ###
    ### Nested functions
    ###

    def get_empty_nested_positions(self):
        '''
        Function to get the array of nested unoccupied positions
        '''
        nested = []
        for i in range(88):
            for j in range(45):
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

    def is_surrounded(self, position):
        '''
        Return true if the position is surrounded by pieces
        '''
        neighbors = self.get_neighbor_position(position)
        for neighbor in neighbors:
            if self.board_array[(*(neighbor), 0)] == 0:
                return False
        return True

    def amount_surrounding(self, position):
        '''
        Return the amount of pieces surrounding a position
        '''
        neighbors = self.get_neighbor_position(position)
        amount = 0
        for neighbor in neighbors:
            if self.board_array[(*(neighbor), 0)] != 0:
                amount += 1
        return amount



    def _check_if_inboard(self, position):
        i, j = position[:2]
        if (i < 88) and (j < 45) and (i > 0) and (j > 0):
            return True
        return False


    def get_highest_z(self, position):
        '''
        Get the the z of the highest piece at a given location
        '''
        z = 0
        highest = False
        while z < 5:
            if self.board_array[(*position[:2], z)] == 0:
                z -= 1
                return z if z != -1 else None
            z += 1
        return None


    ###
    ### Pieces movement calculations
    ###


    def get_moving_positions(self, position):
        '''
        Get the right movements positions for the piece located at position
        '''

        if (z := self.get_highest_z(position)) is not None:
            highest_value = self.board_array[(*position[:2], z)]
        else:
            highest_value = self.board_array[(*position[:2], 4)]
        highest_bug_name = name_dic[highest_value]


        # Remove the piece during calculations since she's in movement
        self.board_array[(*position,)] = 0


        if highest_bug_name == "ant":
            positions = self._get_ant_moving_positions(position)
        elif highest_bug_name == "spider":
            positions = self._get_spider_moving_positions(position)
        elif highest_bug_name == "bee":
            positions = self._get_bee_moving_positions(position)
        elif highest_bug_name == "grasshopper":
            positions = self._get_grasshopper_moving_positions(position)
        elif highest_bug_name == "beetle":
            positions = self._get_beetle_moving_positions(position)
        else:
            positions = self.get_neighbor_sliding(position)

        # Replace the piece after calculations
        self.board_array[(*position,)] = highest_value

        # Remove the piece position since it doesn't change game state
        if position in positions:
            positions.remove(position)

        return positions

    def _get_beetle_moving_positions(self, position):
        '''
        Beetle calculator
        '''
        positions = []

        raw_neighbors = self.get_neighbor_position(position)
        # Array containing the positions of the highest neighbors if occupied
        highest_occupied_neighbors = []
        for raw_neighbor in raw_neighbors:
            if (z := self.get_highest_z(raw_neighbor)) is not None:
                highest_occupied_neighbors.append([*raw_neighbor, z])


        for occupied_neighbor in highest_occupied_neighbors:
            previous_values = self.board_array[occupied_neighbor[0],
                                               occupied_neighbor[1], :].copy()
            # We remove where we want to climb
            self.board_array[occupied_neighbor[0], occupied_neighbor[1], :] = [0, 0, 0, 0, 0]

            # If it is possible to slide there by being one z above, it means we can climb it
            hypothetic_slides = self.get_neighbor_sliding([*position[:2], occupied_neighbor[2] + 1])

            # We replace what we removed
            self.board_array[occupied_neighbor[0], occupied_neighbor[1], :] = previous_values.copy()


            # We add the position with one more z if it is possible
            if [*occupied_neighbor[:2], occupied_neighbor[2] + 1] in hypothetic_slides:
                positions.append([*occupied_neighbor[:2], occupied_neighbor[2] + 1])

        # We then calculate the classics slides at the z of the beetle
        classic_slide_z = self.get_neighbor_sliding(position)
        for i, slide in enumerate(classic_slide_z):
            # We check if there's a piece
            if (z := self.get_highest_z(slide)) is not None:
                # If yes, the real slide must go just above the piece (z+1)
                classic_slide_z[i] = [*slide[:2], z+1]
            else:
                # If not, the real slide is 0
                classic_slide_z[i] = [*slide[:2], 0]

        for position in classic_slide_z:
            if position not in positions:
                positions.append(position)

        return positions

    def _get_grasshopper_moving_positions(self, position):
        '''
        Grasshopper calculator
        '''
        def find_empty_in_line(i, j):
            found_position = position.copy()
            while self.board_array[(
                found_position[0]+i,
                found_position[1]+j,
                0)] != 0:
                found_position[0] += i
                found_position[1] += j
            found_position[0] += i
            found_position[1] += j
            return found_position

        possibles_hops = [
            find_empty_in_line(2, 0),
            find_empty_in_line(-2, 0),
            find_empty_in_line(1, 1),
            find_empty_in_line(1, -1),
            find_empty_in_line(-1, -1),
            find_empty_in_line(-1, 1),
        ]
        positions = [hop
                     for hop in possibles_hops
                     if hop[:2] not in self.get_neighbor_position(position)]
        return positions



    def _get_bee_moving_positions(self, position):
        '''
        Bee calculator
        '''
        return self.get_neighbor_sliding(position)

    def _get_spider_moving_positions(self, position):
        '''
        Spider calculator
        '''
        slide_positions_1 = [self.get_neighbor_sliding(position),
                             position]
        slide_positions_2 = []
        slide_positions_3 = []

        # Find positions with 2 slides
        for position_1 in slide_positions_1[0]:
            new_slide_2_positions = self.get_neighbor_sliding(position_1)


            # Remove Backtrack
            new_slide_2_positions.remove(slide_positions_1[1])

            # Position 1 is the position that generated these positions
            # We keep it to remove backtrack in the last step
            slide_positions_2.append([new_slide_2_positions,
                                     position_1])


        # Find positions with 3 slides
        for trajectory in slide_positions_2:
            for position_2 in trajectory[0]:
                new_slide_3_positions = self.get_neighbor_sliding(position_2)
                # Remove backtrack
                new_slide_3_positions.remove(trajectory[1])

                for position_3 in new_slide_3_positions:
                    if position_3 not in slide_positions_3:
                        slide_positions_3.append(position_3)


        return slide_positions_3

    def _get_ant_moving_positions(self, position, movements=[]):
        '''
        Ant calculator
        '''
        n = len(movements)
        if n == 0:
            movements = self.get_neighbor_sliding(position)
        else:
            # We add the sliding neighbor of each sliding neighbor
            for movement in movements:
                new_movements = self.get_neighbor_sliding(movement)

                for new_movement in new_movements:
                    if not new_movement in movements:
                        movements.append(new_movement)
        if len(movements) > n:
            # If we got new positions, we continue
            return self._get_ant_moving_positions(position, movements)
        return movements
