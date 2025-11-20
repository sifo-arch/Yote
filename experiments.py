from easyAI import TwoPlayerGame
import numpy as np


class Yote(TwoPlayerGame):
    def __init__(self, players):
        self.players = players
        # the white player is always the first on the list of players and the first to play
        self.nplayer = 1
        
        # the representation of possible states of a position on the board
        self.__white_pos = 1
        self.__black_pos = -1
        self.__empty_pos = 0
        # the board of the game is empty at the beginning
        self.__board = np.zeros((5, 6), dtype=np.int32)
        # the number of white stones in hand of the white player
        self.__num_of_white_stones = 12
        # the number of black stones in hand of the black player
        self.__num_of_black_stones = 12

    def __empty_board_positions(self):
        """
        Returns the indices of empty positions on the board
        """
        i_indices, j_indices = np.where(self.__board == self.__empty_pos)
        return list(zip(i_indices, j_indices))
    

    def __get_stone_adjacents(self, stone_pos, return_dict=False):
        """
        Returns the adjacents of a stone
        """
        i, j = stone_pos
        adjacents = []
        keys = []
        if i > 0:
            adjacents.append((i - 1, j)) # top adjacent
            keys.append('top')
        if i < 4:
            adjacents.append((i + 1, j)) # bottom adjacent
            keys.append('bottom')
        if j > 0:
            adjacents.append((i, j - 1)) # left adjacent
            keys.append('left')
        if j < 5:
            adjacents.append((i, j + 1)) # right adjacent
            keys.append('right')
        return dict(zip(keys, adjacents)) if return_dict else adjacents
    

    def __get_stone_empty_adjacents(self, stone_pos, return_dict=None):
        """
        Returns the adjacent positions of a stone that are empty
        """
        adjacents = self.__get_stone_adjacents(stone_pos)
        empty_adjacents = []
        for adjacent in adjacents:
            i, j = adjacent
            if self.__board[i, j] == self.__empty_pos:
                empty_adjacents.append(adjacent)
        return empty_adjacents
    

    def __get_my_stones_positions(self):
        """
        Returns the positions on the board of the stones of the current player
        """
        positions = None
        if self.nplayer == 1:
            positions = np.where(self.__board == self.__white_pos)
        else:
            positions = np.where(self.__board == self.__black_pos)
        i_indices, j_indices = positions
        return list(zip(i_indices, j_indices))


    def __get_opponent_adjacent_stones(self, stone_pos):
        """
        Returns stones of the opponent player that are adjacent to a stone of the current player
        """
        adjacents = self.__get_stone_adjacents(stone_pos, return_dict=True)
        opponent_stone = self.__black_pos if self.nplayer == 1 else self.__white_pos
        adjacent_opponent_stones = {}
        for pos in adjacents:
            i, j = adjacents[pos]
            if self.__board[i, j] == opponent_stone:
                adjacent_opponent_stones[pos] = adjacents[pos]
        return adjacent_opponent_stones
    

    def __possible_captures_of_a_stone(self, stone_pos):
        opponent_adjacent_stones = self.__get_opponent_adjacent_stones(stone_pos)
        poss_captures = []
        for direction in opponent_adjacent_stones:
            i, j = opponent_adjacent_stones[direction]
            dest_i_after_capture = None
            dest_j_after_capture = None
            if direction == "top" and i > 0:
                dest_i_after_capture = i - 1
                dest_j_after_capture = j
            elif direction == "bottom" and i < 4:
                dest_i_after_capture = i + 1
                dest_j_after_capture = j
            elif direction == "left" and j > 0:
                dest_i_after_capture = i
                dest_j_after_capture = j - 1
            elif direction == "right" and j < 5:
                dest_i_after_capture = i
                dest_j_after_capture = j + 1
            # conditions must be satisfied to allow capturing
            cond1 = dest_i_after_capture is not None
            cond2 = dest_j_after_capture is not None
            cond3 = self.__board[dest_i_after_capture, dest_j_after_capture] == self.__empty_pos
            if cond1 and cond2 and cond3:
                poss_captures.append((dest_i_after_capture, dest_j_after_capture))
        return poss_captures


    def possible_moves(self):
        # a list as possile moves container
        poss_moves = []
        # rule-1: if the current player still has stones in his/her hand, he/she could place a stone on an empty position on the board.
        empty_board_positions = []
        if (self.nplayer == 1 and self.__num_of_white_stones > 0) or (self.nplayer == 2 and self.__num_of_black_stones > 0):
            empty_board_positions = [((i, j), 'h') for i, j in self.__empty_board_positions()]  # h stands for hand, it means the player can place a stone from his/her hand on an empty position on the board.
        
        poss_moves.extend(empty_board_positions)

        # rule-2: if the current player has stones that were previously placed on the board, he/she could move them orthogonally if possible.
        my_stones_positions = self.__get_my_stones_positions()
        empty_positions_to_move_stones = []
        for stone_pos in my_stones_positions:
            empty_positions_to_move_stones.extend([((i, j), 'b') for i, j in self.__get_stone_empty_adjacents(stone_pos)])  # b stands for board, it means a player can move one of his/her stones that are already on the board to another position.
        
        poss_moves.extend(empty_positions_to_move_stones)

        # rule-3: capturing (see the section 'Rules' in https://en.wikipedia.org/wiki/Yot%C3%A9)
        possible_captures = []
        for stone_pos in my_stones_positions:
            possible_captures.extend([((i, j), 'c') for i, j in self.__possible_captures_of_a_stone(stone_pos)])  # c stands for capture, it means a player can capture an opponent's stone on the board according to rule-3
        
        poss_moves.extend(possible_captures)
        
        return poss_moves


    def make_move(self, move):
        pass


    def is_over(self):
        pass


    def test(self):
        print(self.__empty_board_positions())
    

if __name__ == "__main__":
    game = Yote(None)
    game.test()
        