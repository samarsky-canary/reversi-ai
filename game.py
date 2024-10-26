from color import Color
from copy import deepcopy
import rules


def session(board: list[list[Color]], first_bot, second_bot) -> dict:
    protocol = {
        "first bot": first_bot.__name__,
        "second bot": second_bot.__name__,
        "details": []
    }

    name_deque = [first_bot.__name__, second_bot.__name__]
    first_bot = first_bot.bot_turn
    second_bot = second_bot.bot_turn
    turn_deque = [first_bot, second_bot]
    color_deque = [Color.BLACK, Color.WHITE]
    turn_index = 0

    first_stopped = False

    while True:
        current_bot = turn_deque[turn_index]
        current_color = color_deque[turn_index]

        fields = rules.available_fields(board, current_color)
        # Отсутствие доступных ходов у бота
        if len(fields) == 0:
            protocol["details"].append(f"Бот {name_deque[turn_index]} не может выполнить ход")
            # Его оппонент перед этим был в такой же ситуации
            if not first_stopped:
                first_stopped = True
                turn_index = (turn_index + 1) % 2
                continue
            else:
                protocol["details"].append("Оба бота не могут выполнить ход")
                protocol["details"].append("Игра окончена")
                break

        old_board = deepcopy(board)
        chosen_field = current_bot(board, current_color)
        print("({}, {})".format(chosen_field[0], chosen_field[1]))
        if chosen_field is not None:
            protocol["details"].append(
                f"Бот {name_deque[turn_index]} выполняет ход {chosen_field} цветом {current_color}")
        else:
            protocol["details"].append(f"Бот {name_deque[turn_index]} не выполнил ход")

        if rules.board_diff(old_board, board) or not rules.check_field_validness(chosen_field) \
                or (chosen_field is None and len(fields) != 0) or not rules.turn_validness(chosen_field, fields):
            protocol["details"].append(f"Бот {name_deque[turn_index]} совершил ошибку")
            protocol["details"].append("Игра окончена")
            turn_index = (turn_index + 1) % 2
            winner = protocol["first bot"] if turn_index == 0 else protocol["second bot"]
            protocol["winner"] = winner
            return protocol

        board[chosen_field[0]][chosen_field[1]] = current_color

        rules.redraw(board, chosen_field, current_color, protocol)

        turn_index = (turn_index + 1) % 2

        first_stopped = False

    color_counts = rules.count_fields(board)
    winner = "draw"
    protocol["details"].append(
        f"Было закрашено {color_counts[Color.BLACK]} полей черным цветом, {color_counts[Color.WHITE]} полей белым цветом")
    if color_counts[Color.BLACK] > color_counts[Color.WHITE]:
        winner = protocol["first bot"]
    if color_counts[Color.BLACK] < color_counts[Color.WHITE]:
        winner = protocol["second bot"]
    protocol["winner"] = winner
    return protocol
