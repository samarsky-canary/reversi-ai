from color import Color
from copy import deepcopy
import rules

def session(board: list[list[Color]], first_bot, second_bot) -> dict:
    turn_deque = [first_bot, second_bot]
    color_deque = [Color.BLACK, Color.WHITE]
    turn_index = 0
    first_stopped = False

    while True:
        current_bot = turn_deque[turn_index]
        current_color = color_deque[turn_index]

        fields = rules.available_fields(board, current_color)
        if len(fields) == 0:
            if not first_stopped:
                first_stopped = True
                turn_index = (turn_index + 1) % 2
                continue
            else:
                break
            
        old_board = deepcopy(board)
        chosen_field = current_bot(board, current_color)

        if rules.board_diff(old_board, board) or not rules.check_field_validness(chosen_field) \
            or chosen_field is None and len(fields) != 0 or not rules.turn_validness(chosen_field, fields):
            turn_index = (turn_index + 1) % 2
            winner = "first bot" if turn_index == 0 else "second bot"
            return {"winner" : winner}

        board[chosen_field[0]][chosen_field[1]] = current_color
        rules.redraw(board, chosen_field, current_color)
        turn_index = (turn_index + 1) % 2
    
    color_counts = rules.count_fields(board)
    winner = "draw"
    if color_counts[Color.BLACK] > color_counts[Color.WHITE]:
        winner = "first bot"
    if color_counts[Color.BLACK] < color_counts[Color.WHITE]:
        winner = "second bot"
    return {"winner" : winner}
