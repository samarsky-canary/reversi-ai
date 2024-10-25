from game import session
from color import Color
import importlib
import pkgutil
import random

discovered_bots = [
    (owner, importlib.import_module(owner))
    for finder, owner, ispkg
    in pkgutil.iter_modules()
    if owner.startswith('bot_')
]

# random.shuffle(discovered_bots)

for k in range(0, len(discovered_bots) // 2 * 2, 1):
    board = [[Color.EMPTY for j in range(8)] for i in range(8)]
    board[3][4] = Color.BLACK
    board[4][3] = Color.BLACK
    board[3][3] = Color.WHITE
    board[4][4] = Color.WHITE
    print(discovered_bots[k][1].__name__, "vs", discovered_bots[k + 1][1].__name__)
    result = session(board, discovered_bots[k][1].bot_turn, discovered_bots[k + 1][1].bot_turn)
    print(result)