from enum import IntEnum

NEIGHBOUR_MATRIX = [(-1, 0), (-1, -1), (0, -1), (1, -1), (1, 0), (1, 1), (0, 1), (-1, 1)]


class Directions(IntEnum):
    UP = 0
    LEFT = 1
    DOWN = 2
    RIGHT = 3
