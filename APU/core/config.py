from pathlib import Path
import pygame as pg

TILE_SIZE = 16

D_WIDTH = 1280
D_HEIGHT = 720

IDLE = 0
NORTH = 1
EAST = 2
SOUTH = 3
WEST = 4

DEFAULT_FPS = 60
ASSETSPATH = f"{Path.cwd()}\\assets"

KEYMAP = {
    pg.K_w: NORTH,
    pg.K_a: WEST,
    pg.K_s: SOUTH,
    pg.K_d: EAST
}
