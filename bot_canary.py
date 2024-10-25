import math
from collections import OrderedDict
from copy import deepcopy
from enum import Enum

from color import Color


def bot_turn(ed_board: list[list[Color]], ed_color: Color) -> tuple[int, int]:
    new_board = OrderedDict((Cord(i, j), Color.EMPTY) for i in range(8) for j in range(8))

    for i in range(8):
        for j in range(8):
            new_board[Cord(i, j)] = ed_board[i][j]

    game = Game(new_board, ed_color)
    move: Cord = BotAi.get_next_move(game, ed_color)
    return move.x, move.y

# ===================================================================================
# Coordinates
# ===================================================================================
class GameState(Enum):
    IN_PROGRESS = 0
    BLACK_WINS = 1
    WHITE_WINS = 2
    DRAW = 3
# ===================================================================================
# Coordinates
# ===================================================================================
class Cord():

    # on difinition we pass x and y values to class
    def __init__(self, x, y):
        self.x = x
        self.y = y

    # gets two cordinations and returns the sum of them as new Coord
    def __add__(self, other):
        return Cord(self.x + other.x, self.y + other.y)

    # compares two Coords
    def __eq__(self, other):
        return self.x == other.x and self.y == other.y

    def __ne__(self, other):
        return self.x != other.x or self.y != other.y

    def __hash__(self):
        return hash((self.x, self.y))

    # string representaition of object
    def __str__(self):
        return "({}, {})".format(self.x, self.y)

    # defines if Coord is in right domain
    def is_in_board(self):
        return min(self.x, self.y) >= 0 and max(self.x, self.y) < 8

    # maybe related to flipping
    def to(self, end, step):
        if (end.x - self.x) * step.y != (end.y - self.y) * step.x:
            raise Exception("Invalid cords")

        result = []
        coord = self
        while coord != end:
            result.append(coord)
            coord += step
        return result

# ===================================================================================
# Game
# ===================================================================================
class Game:
    # surronding of a stone
    DIRECTIONS = [Cord(x, y)
                  for x, y in [(-1, -1), (-1, 0), (0, -1), (1, -1), (-1, 1), (0, 1), (1, 0), (1, 1)]]

    def __init__(self, board = None, player = None):

        # creating the board as 64 tiles
        self.board = OrderedDict((Cord(i, j), Color.EMPTY) for i in range(8) for j in range(8))

        if board is None:
            self.board[Cord(3, 3)] = Color.WHITE
            self.board[Cord(4, 4)] = Color.WHITE
            self.board[Cord(3, 4)] = Color.BLACK
            self.board[Cord(4, 3)] = Color.BLACK
        else:
            self.board = deepcopy(board)

        if player is None:
            self.current_player = Color.BLACK
        else:
            self.current_player = player
        # creating initial scores

        self.whites = len(self.colored_fields(Color.WHITE))
        self.blacks = len(self.colored_fields(Color.BLACK))
        self.game_state = self.outcome()

    def enemy_color(self):
        return Color.BLACK if self.current_player == Color.WHITE else Color.WHITE

    # determines if the disk in the given coordination is current players or not
    def is_enemy_field(self, cord):
        return (cord.is_in_board() and
                self.board[cord] not in [self.current_player, Color.EMPTY])

    def is_friend_field(self, cord):
        return cord.is_in_board() and self.board[cord] == self.current_player

    # checking if the disc is empty
    def is_empty_field(self, coord):
        return coord.is_in_board() and self.board[coord] == Color.EMPTY

    # returns an array of all current player discs
    def friend_fields(self):
        fields = [Cord(i, j) for i in range(8) for j in range(8)]
        return [cord for cord in fields if self.board[cord] == self.current_player]

    # array of black player discs
    def enemy_fields(self):
        enemy_color = self.enemy_color()
        fields = [Cord(i, j) for i in range(8) for j in range(8)]
        return [cord for cord in fields if self.board[cord] == enemy_color]

    def colored_fields(self, color: Color):
        fields = [Cord(i, j) for i in range(8) for j in range(8)]
        return [cord for cord in fields if self.board[cord] == color]

    # changes the turn
    def change_player(self):
        self.current_player = self.enemy_color()

    # array of clickable cordinations
    def available_moves(self):
        friends = self.friend_fields()
        av_fields = []
        for friend in friends:
            for direction in self.DIRECTIONS:
                field = friend + direction
                while self.is_enemy_field(field):
                    field += direction
                    if self.is_empty_field(field):
                        av_fields += [field]
        return av_fields

    # if coordination is in available fields
    def is_valid_move(self, cord):
        return cord in self.available_moves()

    def is_game_over(self):
        return self.game_state != GameState.IN_PROGRESS

    def play(self, move):
        if self.is_game_over():
            raise Exception('Game has already ended')
        if not self.is_valid_move(move):
            raise Exception("Not valid move")

        # fields that are flipped after a move
        won_fields = []
        for direction in self.DIRECTIONS:
            field = move + direction
            while self.is_enemy_field(field):
                field += direction

            if self.is_friend_field(field):
                won_fields += move.to(field, direction)

        # change the field to the player's field
        for move in won_fields:
            self.board[move] = self.current_player

        # update player result after each move
        self.blacks = len(self.colored_fields(Color.BLACK))
        self.whites = len(self.colored_fields(Color.WHITE))
        self.change_player()
        self.game_state = self.outcome()

    # run after every move
    def outcome(self):
        # change player if there is no move for first player
        if not self.available_moves():
            self.change_player()

            # if second player had no move determine the winner
            if not self.available_moves():
                if self.whites > self.blacks:
                    return GameState.WHITE_WINS
                elif self.whites < self.blacks:
                    return GameState.BLACK_WINS
                else:
                    return GameState.DRAW
        return GameState.IN_PROGRESS

    @staticmethod
    def print_color(color: Color):
        if color == Color.BLACK:
            return 'o'
        if color == Color.WHITE:
            return 'x'
        return ' '

    # returns a string of current board situation
    @staticmethod
    def print_board(board):
        output = ''
        for i in range(8):
            colors = []
            for j in range(8):
                colors.append(Game.print_color(board[i][j]))

            output = '\n'.join(colors)
        return output

class FormatConverter:

    @staticmethod
    def ai_to_game_board(ai_board):
        return OrderedDict((Cord(i, j), ai_board[i][j])
                           for i in range(8) for j in range(8))

    @staticmethod
    def game_to_ai_board(game_board):
        return [[game_board[Cord(i, j)] for j in range(8)] for i in range(8)]


class BotAi:

    # finding available moves
    @staticmethod
    def available_moves(board, player):
        game = Game(board, player)
        return game.available_moves()


    # runs the minimax with precision
    @staticmethod
    def get_next_move(game: Game, color) -> Cord:
        # the depth argument defines how many levels deep we go before using heuristic
        (df, move) = BotAi.minimax(game.board, 2, color, color)
        return move

    @staticmethod
    def minimax(board, depth, player, original_player):
        game = Game(board, player)
        # if game is over then return something
        if game.is_game_over() or depth == 0:
            return BotAi.game_heuristic(board, original_player), None

        best_move = None

        max_player = player == original_player
        # if it is a max node
        if max_player:
            best_value = -math.inf
            available_moves = game.available_moves()
            for move in available_moves:
                game_bckp = deepcopy(game)
                game.play(move)
                value, _ = BotAi.minimax(game.board, depth - 1, game.current_player, original_player)
                game = game_bckp #revert move
                if value > best_value:
                    best_value = value
                    best_move = move
            return best_value, best_move

        # if it is a min node
        else:
            best_value = math.inf
            available_moves = game.available_moves()
            for move in available_moves:
                game_bckp = deepcopy(game)
                game.play(move)
                value, _ = BotAi.minimax(game.board, depth - 1, game.current_player, original_player)
                game = game_bckp # revert move
                if value < best_value:
                    best_value = value
                    best_move = move
            return best_value, best_move

    @staticmethod
    def game_heuristic(board, player):
        # defining the ai and Opponent color
        my_color = player
        opp_color = Color.WHITE if player == Color.BLACK else Color.BLACK

        my_tiles = 0
        opp_tiles = 0
        my_front_tiles = 0
        opp_front_tiles = 0

        p = 0
        c = 0
        l = 0
        m = 0
        f = 0
        d = 0

        # these two are used for going in every 8 directions
        X1 = [-1, -1, 0, 1, 1, 1, 0, -1]
        Y1 = [0, 1, 1, 1, 0, -1, -1, -1]

        V = [
            [20, -3, 11,  8,  8, 11, -3, 20],
            [-3, -7, -4,  1,  1, -4, -7, -3],
            [11, -4,  2,  2,  2,  2, -4, 11],
            [8,   1,  2, -3, -3,  2,  1,  8],
            [8,   1,  2, -3, -3,  2,  1,  8],
            [11, -4,  2,  2,  2,  2, -4, 11],
            [-3, -7, -4,  1,  1, -4, -7, -3],
            [20, -3, 11,  8,  8, 11, -3, 20]
        ]

        # =============================================================================================
        # 1- Piece difference, frontier disks and disk squares
        # =============================================================================================
        for i in range(8):
            for j in range(8):
                if board[Cord(i,j)] == my_color:
                    d += V[i][j]
                    my_tiles += 1
                elif board[Cord(i,j)] == opp_color:
                    d -= V[i][j]
                    opp_tiles += 1

                # calculates the number of blank spaces around me
                # if the tile is not empty take a step in each direction
                if board[Cord(i,j)] != Color.EMPTY:
                    for k in range(8):
                        x = i + X1[k]
                        y = j + Y1[k]
                        if (0 <= x < 8 and 0 <= y < 8 and
                                board[Cord(i,j)] == Color.EMPTY):
                            if board[Cord(i,j)] == my_color:
                                my_front_tiles += 1
                            else:
                                opp_front_tiles += 1
                            break

        # =============================================================================================
        # 2 - calculates the difference between current colored tiles
        # =============================================================================================
        if my_tiles > opp_tiles:
            p = (100.0 * my_tiles) / (my_tiles + opp_tiles)
        elif my_tiles < opp_tiles:
            p = -(100.0 * opp_tiles) / (my_tiles + opp_tiles)
        else:
            p = 0

        # =============================================================================================
        # 3- calculates the blank Spaces around my tiles
        # =============================================================================================
        if my_front_tiles > opp_front_tiles:
            f = -(100.0 * my_front_tiles) / (my_front_tiles + opp_front_tiles)
        elif my_front_tiles < opp_front_tiles:
            f = (100.0 * opp_front_tiles) / (my_front_tiles + opp_front_tiles)
        else:
            f = 0

        # ===============================================================================================
        # 4 - Corner occupancy
        '''
        Examine all 4 corners :
        if they were my color add a point to me 
        if they were enemies add a point to the enemy
        '''
        # ===============================================================================================
        my_tiles = opp_tiles = 0
        if board[Cord(0,0)] == my_color:
            my_tiles += 1
        elif board[Cord(0,0)] == opp_color:
            opp_tiles += 1
        if board[Cord(0,7)] == my_color:
            my_tiles += 1
        elif board[Cord(0,7)] == opp_color:
            opp_tiles += 1
        if board[Cord(7,0)] == my_color:
            my_tiles += 1
        elif board[Cord(7,0)] == opp_color:
            opp_tiles += 1
        if board[Cord(7,7)] == my_color:
            my_tiles += 1
        elif board[Cord(7,7)] == opp_color:
            opp_tiles += 1
        c = 25 * (my_tiles - opp_tiles)

        # ===============================================================================================
        # 5 - CORNER CLOSENESS
        '''
        If the corner is empty then find out how many of the 
        adjacent block to the corner are AI's or the player's
        if AI's tiles were mote than players than it's a bad thing.
        '''
        # ===============================================================================================
        my_tiles = opp_tiles = 0
        if board[Cord(0,0)] == Color.EMPTY:
            if board[Cord(0,1)] == my_color:
                my_tiles += 1
            elif board[Cord(0,1)] == opp_color:
                opp_tiles += 1
            if board[Cord(1,1)]== my_color:
                my_tiles += 1
            elif board[Cord(1,1)] == opp_color:
                opp_tiles += 1
            if board[Cord(1,0)] == my_color:
                my_tiles += 1
            elif board[Cord(1,0)] == opp_color:
                opp_tiles += 1

        if board[Cord(0,7)] == ' ':
            if board[Cord(0,6)] == my_color:
                my_tiles += 1
            elif board[Cord(0,6)] == opp_color:
                opp_tiles += 1
            if board[Cord(1,6)] == my_color:
                my_tiles += 1
            elif board[Cord(1, 6)] == opp_color:
                opp_tiles += 1
            if board[Cord(1, 7)] == my_color:
                my_tiles += 1
            elif board[Cord(1, 7)] == opp_color:
                opp_tiles += 1

        if board[Cord(7,0)] == ' ':
            if board[Cord(7,1)] == my_color:
                my_tiles += 1
            elif board[Cord(7,1)] == opp_color:
                opp_tiles += 1
            if board[Cord(6,1)] == my_color:
                my_tiles += 1
            elif board[Cord(6,1)] == opp_color:
                opp_tiles += 1
            if board[Cord(6,0)] == my_color:
                my_tiles += 1
            elif board[Cord(6,0)] == opp_color:
                opp_tiles += 1

        if board[Cord(7,7)] == Color.EMPTY:
            if board[Cord(6,7)] == my_color:
                my_tiles += 1
            elif board[Cord(6,7)] == opp_color:
                opp_tiles += 1
            if board[Cord(6,6)] == my_color:
                my_tiles += 1
            elif board[Cord(6,6)] == opp_color:
                opp_tiles += 1
            if board[Cord(7,6)] == my_color:
                my_tiles += 1
            elif board[Cord(7,6)] == opp_color:
                opp_tiles += 1

        l = -12.5 * (my_tiles - opp_tiles)

        # ===============================================================================================
        # 6 - Mobility
        # ===============================================================================================
        '''
        It attempts to capture the relative difference between 
        the number of possible moves for the max and the min players,
        with the intent of restricting the
        opponent’s mobility and increasing one’s own mobility
        '''
        # basically it calculates the difference between available moves
        my_tiles = len(BotAi.available_moves(board, my_color))
        opp_tiles = len(BotAi.available_moves(board, opp_color))

        if my_tiles > opp_tiles:
            m = (100.0 * my_tiles) / (my_tiles + opp_tiles)
        elif my_tiles < opp_tiles:
            m = -(100.0 * opp_tiles) / (my_tiles + opp_tiles)
        else:
            m = 0

        # =============================================================================================
        # =============================================================================================
        # final weighted score
        # adding different weights to different evaluations
        return (10 * p) + (801.724 * c) + (382.026 * l) + \
               (78.922 * m) + (74.396 * f) + (10 * d)
