from collections import OrderedDict

from color import Color

# ===================================================================================
# coordination
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

        if (board is None):
            self.board[Cord(3, 3)] = Color.WHITE
            self.board[Cord(4, 4)] = Color.WHITE
            self.board[Cord(3, 4)] = Color.BLACK
            self.board[Cord(4, 3)] = Color.BLACK

        # creating initial scores
        self.game_state = self.outcome()

    # determines if the disk in the given coordination is current players or not
    def is_enemy_disc(self, coord):
        return (coord.is_in_board() and
                self.board[coord] not in [self.player.field, self.EMPTY])

    def is_ally_disc(self, coord):
        return coord.is_in_board() and self.board[coord] == self.player.field


    # checking if the disc is empty
    def is_empty_disc(self, coord):
        return coord.is_in_board() and self.board[coord] == self.EMPTY

    # returns an array of all current player discs
    def current_player_discs(self):
        all_coords = [Cord(i, j) for i in range(8) for j in range(8)]
        return [coord for coord in all_coords
                if self.board[coord] == self.player.field]

    # array of black player discs
    def black_player_discs(self):
        all_coords = [Cord(i, j) for i in range(8) for j in range(8)]
        return [coord for coord in all_coords
                if self.board[coord] == self.black_player.field]

    # array of white player discs
    def white_player_discs(self):
        all_coords = [Cord(i, j) for i in range(8) for j in range(8)]
        return [coord for coord in all_coords
                if self.board[coord] == self.white_player.field]

    # changes the turn
    def change_current_player(self):
        if self.player == self.black_player:
            self.player = self.white_player
        else:
            self.player = self.black_player

    # array of clickable cordinations
    def available_fields(self):
        discs = self.current_player_discs()
        result = []
        for disc in discs:
            for d in self.DIRECTIONS:
                coord = disc + d
                while self.is_enemy_disc(coord):
                    coord += d
                    if self.is_empty_disc(coord):
                        result += [coord]
        return result

    # if coordination is in available fileds
    def is_valid_move(self, coord):
        return coord in self.available_fields()

    def play(self, coord):
        if self.game_state != self.GAME_STATES['IN_PROGRESS']:
            raise GameHasEndedError('Game has already ended')
        if not self.is_valid_move(coord):
            raise InvalidMoveError("Not valid move")

        # fields that are flipped after a move
        won_fields = []
        for d in self.DIRECTIONS:
            current_coord = coord + d
            while self.is_enemy_disc(current_coord):
                current_coord += d

            if self.is_ally_disc(current_coord):
                won_fields += coord.to(current_coord, d)

        # change the field to the player's field
        for coord in won_fields:
            self.board[coord] = self.player.field

        # update player result after aech move
        self.black_player.result = len(self.black_player_discs())
        self.white_player.result = len(self.white_player_discs())
        self.change_current_player()
        self.game_state = self.outcome()

    # run after every move
    def outcome(self):
        # change player if there is no move for first player
        if not self.available_fields():
            self.change_current_player()

            # if second player had no move determine the winner
            if not self.available_fields():
                if self.white_player.result > self.black_player.result:
                    return self.GAME_STATES["WHITE_WINS"]
                elif self.white_player.result < self.black_player.result:
                    return self.GAME_STATES["BLACK_WINS"]
                else:
                    return self.GAME_STATES["DRAW"]
        return self.GAME_STATES["IN_PROGRESS"]

    # returns a string of current board situation
    @staticmethod
    def print_board(board):
        return '\n'.join(''.join(board[Cord(i, j)] for j in range(8))
                         for i in range(8))

    # information to show about the current game
    def game_info(self):
        player_map = {
            "b": "black",
            "w": "white",
            "m": "moves"
        }
        board = self.board.copy()
        moves = self.available_fields()
        for move in moves:
            board[move] = self.MOVES

        return {
            "board": self.print_board(board),
            "player": player_map[self.player.field],
            "state": self.game_state,
            "white_count": self.white_player.result,
            "black_count": self.black_player.result
        }


def bot_turn(board: list[list[Color]], ed_color: Color) -> tuple[int, int]:
    print(board)

    game = Game()
    for i in range(8):
        for j in range(8):
            color = game.EMPTY
            if board[i][j] == Color.BLACK:
                color = game.BLACK
            elif board[i][j] == Color.WHITE:
                color = game.WHITE
            game.board[Cord(i,j)] = color
    conv_color = 'w'
    if ed_color == Color.BLACK:
        conv_color = 'b'
    _, move = BotAi.minimax(game.board, 3, conv_color)

    for i in range(8):
        for j in range(8):
            if Cord(i,j) == move:
                return (i,j)
    return (-1, -1)


class AIHelper():
    MAX_PLAYER = 'w'
    MIN_PLAYER = 'b'
    INFINITY = 1.0e+10

    """
    Helper interface class for the AI
        $1. available moves (board, player)
        $2. get_resulting_board -> (board, player, coord)
        $3. player pools (board, player)
        $4. check if game has ended (board)
    """

    # it is created when the game starts
    def __init__(self, board=None):
        self.game = Game()
        if board:
            self.set_board(board)

    # changes to board form ai to game board
    def set_board(self, board):
        self.game.board = FormatConverter.ai_to_game_board(board)

    # sets a player
    def set_player(self, player):
        self.game.player = Player(player)

    # finding available moves
    def available_moves(self, board, player):
        self.set_board(board)
        self.set_player(player)
        return self.game.available_fields()

    # gets the changes of the human player
    def get_resulting_board(self, board, player, coord):
        self.set_board(board)
        self.set_player(player)
        self.game.play(coord)
        return FormatConverter.game_to_ai_board(self.game.board)


    def player_pool(self, board, player):
        self.set_board(board)
        # probably this is an error
        return ''.join(''.join(row) for row in self.board).count(player)

    # defines if the game is over or not
    def is_game_over(self, board):
        self.set_board(board)
        return self.game.outcome() != self.game.GAME_STATES["IN_PROGRESS"]


class FormatConverter():

    @staticmethod
    def ai_to_game_board(ai_board):
        return OrderedDict((Cord(i, j), ai_board[i][j])
                           for i in range(8) for j in range(8))

    @staticmethod
    def game_to_ai_board(game_board):
        return [[game_board[Cord(i, j)] for j in range(8)] for i in range(8)]


class BotAi:

    # runs the minimax with precision
    @staticmethod
    def get_next_move(board, color):
        # the depth argument defines how many levels deep we go before using heuristic
        _, move = BotAi.minimax(board, 3, color)
        return move

    @staticmethod
    def minimax(board, depth, player):
        helper = AIHelper()

        # if game is over then return something
        if helper.is_game_over(board) or depth == 0:
            return (BotAi.game_heuristic(board), None)

        best_move = None
        # if it is a max node
        if player == AIHelper.MAX_PLAYER:
            best_value = -AIHelper.INFINITY
            available_moves = helper.available_moves(
                board, AIHelper.MAX_PLAYER)
            for move in available_moves:
                node = helper.get_resulting_board(
                    board, AIHelper.MAX_PLAYER, move)
                value, _ = BotAi.minimax(
                    node, depth - 1, AIHelper.MIN_PLAYER)
                if value > best_value:
                    best_value = value
                    best_move = move
            return (best_value, best_move)

        # if it is a min node
        else:
            best_value = AIHelper.INFINITY
            available_moves = helper.available_moves(
                board, AIHelper.MIN_PLAYER)
            for move in available_moves:
                node = helper.get_resulting_board(
                    board, AIHelper.MIN_PLAYER, move)
                value, _ = BotAi.minimax(
                    node, depth - 1, AIHelper.MAX_PLAYER)
                if value < best_value:
                    best_value = value
                    best_move = move
            return (best_value, best_move)

    @staticmethod
    def game_heuristic(board):
        # defining the ai and Opponent color
        my_color = AIHelper.MAX_PLAYER
        opp_color = AIHelper.MIN_PLAYER

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
                if board[i][j] == my_color:
                    d += V[i][j]
                    my_tiles += 1
                elif board[i][j] == opp_color:
                    d -= V[i][j]
                    opp_tiles += 1

                # calculates the number of blank spaces around me
                # if the tile is not empty take a step in each direction
                if board[i][j] != ' ':
                    for k in range(8):
                        x = i + X1[k]
                        y = j + Y1[k]
                        if (x >= 0 and x < 8 and y >= 0 and y < 8 and
                                board[x][y] == ' '):
                            if board[i][j] == my_color:
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
        if board[0][0] == my_color:
            my_tiles += 1
        elif board[0][0] == opp_color:
            opp_tiles += 1
        if board[0][7] == my_color:
            my_tiles += 1
        elif board[0][7] == opp_color:
            opp_tiles += 1
        if board[7][0] == my_color:
            my_tiles += 1
        elif board[7][0] == opp_color:
            opp_tiles += 1
        if board[7][7] == my_color:
            my_tiles += 1
        elif board[7][7] == opp_color:
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
        if board[0][0] == ' ':
            if board[0][1] == my_color:
                my_tiles += 1
            elif board[0][1] == opp_color:
                opp_tiles += 1
            if board[1][1] == my_color:
                my_tiles += 1
            elif board[1][1] == opp_color:
                opp_tiles += 1
            if board[1][0] == my_color:
                my_tiles += 1
            elif board[1][0] == opp_color:
                opp_tiles += 1

        if board[0][7] == ' ':
            if board[0][6] == my_color:
                my_tiles += 1
            elif board[0][6] == opp_color:
                opp_tiles += 1
            if board[1][6] == my_color:
                my_tiles += 1
            elif board[1][6] == opp_color:
                opp_tiles += 1
            if board[1][7] == my_color:
                my_tiles += 1
            elif board[1][7] == opp_color:
                opp_tiles += 1

        if board[7][0] == ' ':
            if board[7][1] == my_color:
                my_tiles += 1
            elif board[7][1] == opp_color:
                opp_tiles += 1
            if board[6][1] == my_color:
                my_tiles += 1
            elif board[6][1] == opp_color:
                opp_tiles += 1
            if board[6][0] == my_color:
                my_tiles += 1
            elif board[6][0] == opp_color:
                opp_tiles += 1

        if board[7][7] == ' ':
            if board[6][7] == my_color:
                my_tiles += 1
            elif board[6][7] == opp_color:
                opp_tiles += 1
            if board[6][6] == my_color:
                my_tiles += 1
            elif board[6][6] == opp_color:
                opp_tiles += 1
            if board[7][6] == my_color:
                my_tiles += 1
            elif board[7][6] == opp_color:
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
        my_tiles = len(AIHelper().available_moves(board, AIHelper.MAX_PLAYER))
        opp_tiles = len(AIHelper().available_moves(board, AIHelper.MIN_PLAYER))

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
