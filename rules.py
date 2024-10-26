from color import Color

"""
Определяет наличие изменений, сделанных на доске ботом
"""


def board_diff(old: list[list[Color]], current: list[list[Color]]) -> bool:
    for i in range(8):
        for j in range(8):
            if not old[i][j] is current[i][j]:
                return True
    return False


"""
Определяет допустимость хода при известном наборе
"""


def turn_validness(turn_made: tuple[int, int], allowed: list[tuple[int, int]]) -> bool:
    return turn_made in allowed


"""
Возвращает координаты полей, имеющих выбранный цвет
"""


def color_fields(board: list[list[Color]], current_color) -> list[tuple[int, int]]:
    result = []
    for i in range(8):
        for j in range(8):
            if board[i][j] is current_color:
                result.append((i, j))
    return result


"""
Проверяет выход координаты за пределы доски
"""


def check_field_validness(field: tuple[int, int]) -> bool:
    return field is None or (field[0] >= 0 and field[0] < 8 and field[1] >= 0 and field[1] < 8)


"""
Возвращает список координат, куда можно поставить фишку выбранного цвета
"""


def available_fields(board: list[list[Color]], current_color) -> list[tuple[int, int]]:
    result = []
    player_fields = color_fields(board, current_color)
    enemy_color = Color.BLACK if current_color is Color.WHITE else Color.WHITE
    for field in player_fields:
        for direction in [(-1, -1), (-1, 0), (0, -1), (1, -1), (-1, 1), (0, 1), (1, 0), (1, 1)]:
            current_field = (field[0] + direction[0], field[1] + direction[1])
            while check_field_validness(current_field) and board[current_field[0]][current_field[1]] is enemy_color:
                current_field = (current_field[0] + direction[0], current_field[1] + direction[1])
                if check_field_validness(current_field) and board[current_field[0]][current_field[1]] is Color.EMPTY:
                    result.append(current_field)
    return result


"""
Обновляет доску
"""


def redraw(board: list[list[Color]], chosen_field: tuple[int, int], current_color: Color, protocol):
    enemy_color = Color.BLACK if current_color is Color.WHITE else Color.WHITE
    redrawn = []
    for direction in [(-1, -1), (-1, 0), (0, -1), (1, -1), (-1, 1), (0, 1), (1, 0), (1, 1)]:
        current_field = (chosen_field[0] + direction[0], chosen_field[1] + direction[1])
        is_valid = False
        while check_field_validness(current_field) and board[current_field[0]][current_field[1]] is enemy_color:
            current_field = (current_field[0] + direction[0], current_field[1] + direction[1])
            if check_field_validness(current_field) and board[current_field[0]][current_field[1]] is current_color:
                is_valid = True
                break
        if is_valid:
            current_field = (chosen_field[0] + direction[0], chosen_field[1] + direction[1])
            while check_field_validness(current_field) and board[current_field[0]][current_field[1]] is enemy_color:
                board[current_field[0]][current_field[1]] = current_color
                redrawn.append(current_field)
                current_field = (current_field[0] + direction[0], current_field[1] + direction[1])
                if check_field_validness(current_field) and board[current_field[0]][current_field[1]] is current_color:
                    break

    protocol["details"].append(f"Поля {redrawn} перекрашены из {enemy_color} в {current_color}")


"""
Выполняет подсчет полей по цветам
"""


def count_fields(board: list[list[Color]]) -> dict:
    result = {
        Color.BLACK: 0,
        Color.WHITE: 0,
        Color.EMPTY: 0}
    for i in range(8):
        for j in range(8):
            result[board[i][j]] += 1
    return result