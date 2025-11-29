import numpy as np
from __future__ import annotations


class Yote:
    def __init__(self):
        # the white player is always the first on the list of players and the first to play
        self.nplayer = 1
        
        # the representation of possible states of a position on the board
        self.__white_pos = 1
        self.__black_pos = -1
        self.__empty_pos = 0
        # the board of the game is empty at the beginning
        self.__board = np.zeros((5, 6), dtype=np.int32)

        # WHITE PLAYER ATTRIBUTES
        # the number of white stones in hand of the white player
        self.__num_of_white_stones = 12
        # the number of black stones captured by the white player
        self.__white_captures = 0

        # BLACK PLAYER ATTRIBUTES
        # the number of black stones in hand of the black player
        self.__num_of_black_stones = 12
        # the numbe rof white stones captured by the black player
        self.__black_captures = 0

        # scoring (aka evaluation function) weights
        self.__scoring_weights = np.array([0.4, 0.25, 0.15, 0.12, 0.08])


    @property
    def white_pos(self):
        return self.__white_pos
    

    @property
    def black_pos(self):
        return self.__black_pos
    

    @property
    def empty_pos(self):
        return self.__empty_pos
    

    @property
    def board(self):
        return self.__board
    

    @property
    def in_hand_white_stones(self):
        return self.__num_of_white_stones
    

    @property
    def in_hand_black_stones(self):
        return self.__num_of_black_stones
    

    @property
    def white_captures(self):
        return self.__white_captures
    

    @property
    def black_captures(self):
        return self.__black_captures


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
    

    def __get_stone_empty_adjacents(self, stone_pos):
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
    

    def __get_player_stones_positions(self, nplayer):
        """
        Returns the positions on the board of the stones of the current player
        """
        positions = None
        if nplayer == 1:
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
        """
        Returns possible captures of a stone based on its position on the board.
        The function returns the destination position after jumping and the position of the opponent stone to be captured.
        """
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
            if dest_i_after_capture is not None and dest_j_after_capture is not None:
                if self.__board[dest_i_after_capture, dest_j_after_capture] == self.__empty_pos:
                    poss_captures.append(((dest_i_after_capture, dest_j_after_capture), (i, j)))
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
        my_stones_positions = self.__get_player_stones_positions(self.nplayer)
        empty_positions_to_move_stones = []
        for stone_pos in my_stones_positions:
            # (stone_pos, (i, j), 'b'): the format of a possible move according to rule-2
            # b stands for board, it means the current player can move his/her stone in the position stone_pos on the board to the position (i, j).
            empty_positions_to_move_stones.extend([(stone_pos, (i, j), 'b') for i, j in self.__get_stone_empty_adjacents(stone_pos)])  
        
        poss_moves.extend(empty_positions_to_move_stones)

        # rule-3: capturing (see the section 'Rules' in https://en.wikipedia.org/wiki/Yot%C3%A9)
        possible_captures = []
        opponent = 2 if self.nplayer == 1 else 1
        for stone_pos in my_stones_positions:
            # (stone_pos, (i, j), 'c', (l, m)): the format of a possible move according to rule-3 (without choosing an opponent's stone on the board to throw)
            # c stands for capture, it means the current player can move his/her stone on the position stone_pos on the board to the position (i, j) by capturing the opponent's stone which is on the position (l, m)
            stone_poss_captures = [(stone_pos, (i, j), 'c', (l, m)) for (i, j), (l, m) in self.__possible_captures_of_a_stone(stone_pos)]
            if len(stone_poss_captures) > 0:
                # the opponent's stones on the board, one of which can be chosen to throw
                opponent_stones_positions = self.__get_player_stones_positions(nplayer=opponent)
                extended_stone_poss_captures = []
                if len(opponent_stones_positions) > 0:
                    # the new format becomes becomes: (stone_pos, (i, j), 'c', (l, m), (u, v)); where (u, v) is the position on the board of an opponent's stone which can be chosen to throw
                    extended_stone_poss_captures.extend([capture + (to_throw,) for capture in stone_poss_captures for to_throw in opponent_stones_positions if to_throw != capture[3]])
                if len(extended_stone_poss_captures) > 0:
                    possible_captures.extend(extended_stone_poss_captures)
                else:
                    possible_captures.extend(stone_poss_captures)
            
        poss_moves.extend(possible_captures)
        
        return poss_moves


    def __make_move(self, move):
        if 'h' in move:
            i, j = move[0]
            if self.nplayer == 1:
                self.__board[i, j] = self.__white_pos
                self.__num_of_white_stones -= 1
            else:
                self.__board[i, j] = self.__black_pos
                self.__num_of_black_stones -= 1
        elif 'b' in move:
            (src_i, src_j), (des_i, des_j) = move[:2]
            self.__board[src_i, src_j] = self.__empty_pos
            if self.nplayer == 1:
                self.__board[des_i, des_j] = self.__white_pos
            else:
                self.__board[des_i, des_j] = self.__black_pos
        else:
            src_i, src_j = move[0]
            self.__board[src_i, src_j] = self.__empty_pos

            des_i, des_j = move[1]

            captured_i, captured_j = move[3]
            self.__board[captured_i, captured_j] = self.__empty_pos

            if self.nplayer == 1:
                self.__board[des_i, des_j] = self.__white_pos
                self.__white_captures += 1
            else:
                self.__board[des_i, des_j] = self.__black_pos
                self.__black_captures += 1

            if len(move) == 5:
                to_throw_i, to_throw_j = move[4]
                self.__board[to_throw_i, to_throw_j] = self.__empty_pos
                if self.nplayer == 1:
                    self.__white_captures += 1
                else:
                    self.__black_captures += 1


    def play_move(self, move):
        self.__make_move(move)
        # change the turn to the next player
        self.nplayer = 2 if self.nplayer == 1 else 1


    def is_over(self):
        """
        Checks whether the match has finished or not and decides the winner if possible.
        """
        # if either the white or the black player captures all the stones of the opponent, then the game is finihed, and (True, num_of_winner) is returned
        # if the current player can not make any move, then the opponent wins, and (True, num_of_winner) is returned.
        # else the game is not over.
        if self.nplayer == 1:   
            if self.__black_captures == 12 or len(self.possible_moves()) == 0:
                return True, 2
            return False, None
        if self.nplayer == 2:
            if self.__white_captures == 12 or len(self.possible_moves()) == 0:
                return True, 1
            return False, None
    

    def scoring(self):
        possible_moves = self.possible_moves()
        criteria = np.empty(5)
        criteria[1] = len(tuple(filter(lambda move: 'c' in move, possible_moves)))
        criteria[2] = len(possible_moves) - criteria[1]
        if self.nplayer == 1:
            criteria[0] = self.__white_captures
            criteria[3] = 12 - self.__num_of_white_stones
            criteria[4] = self.__num_of_white_stones
        else:
            criteria[0] = self.__black_captures
            criteria[3] = 12 - self.__num_of_black_stones
            criteria[4] = self.__num_of_black_stones
        
        return np.matmul(self.__scoring_weights, criteria)


    def restore(self, state: GameState):
        self.nplayer = state.turn
        self.__board = state.board
        self.__num_of_white_stones = state.white_stones_in_hand
        self.__num_of_black_stones = state.black_stones_in_hand
        self.__white_captures = state.white_captures
        self.__black_captures = state.black_captures


    def test(self):
        print(self.__empty_board_positions())
    

class GameState:
    def __init__(self, game: Yote):
        self.__turn = game.nplayer
        self.__board = game.board.copy()
        self.__white_stones_in_hand = game.in_hand_white_stones
        self.__black_stones_in_hand = game.in_hand_black_stones
        self.__white_captures = game.white_captures
        self.__black_captures = game.black_captures
        self.__scoring = game.scoring()

    
    @property
    def turn(self):
        return self.__turn
    

    @property
    def board(self):
        return self.__board
    

    @property
    def white_stones_in_hand(self):
        return self.__white_stones_in_hand
    

    @property
    def black_stones_in_hand(self):
        return self.__black_stones_in_hand
    

    @property
    def white_captures(self):
        return self.__white_captures
    

    @property
    def black_captures(self):
        return self.__black_captures
    

    @property
    def scoring(self):
        return self.__scoring
    

class History:
    def __init__(self):
        self.__history = []
        self.__counter = 0


    def __assert_history_is_not_empty(self):
        assert self.__counter > 0, "You can't pull from an empty History"

    
    def push(self, state: GameState):
        self.__history.append(state)
        self.__counter += 1
    
    
    def pull(self):
        self.__assert_history_is_not_empty()
        return self.__history[-1]
    

    def pop(self):
        self.__assert_history_is_not_empty()
        state = self.__history.pop()
        self.__counter -= 1
        return state


if __name__ == "__main__":
    game = Yote()
    game.test()
