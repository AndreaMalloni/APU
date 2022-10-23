import pygame as pg
from typing import Sequence
from APU.core.constants import IDLE, NORTH, NORTH_EAST, EAST, SOUTH_EAST, SOUTH, SOUTH_WEST, WEST, NORTH_WEST

def getSurroundingObjects(object, horizontalDistance = 1, verticalDistance = 1, **kwargs: pg.sprite.Group):
        surroundingObjects = []
        for value in kwargs.values():
            surroundingObjects.extend(
                sprite for sprite in value
                if object.rect.inflate(horizontalDistance, verticalDistance).colliderect(sprite.rect))
        return surroundingObjects

def getDirectionFromKeymap(keys: Sequence[bool]) -> int:
    if (keys[pg.K_a] or keys[pg.K_LEFT]) and (keys[pg.K_w] or keys[pg.K_UP]): return NORTH_WEST
    elif (keys[pg.K_d] or keys[pg.K_RIGHT]) and (keys[pg.K_w] or keys[pg.K_UP]): return NORTH_EAST
    elif (keys[pg.K_a] or keys[pg.K_LEFT]) and (keys[pg.K_s] or keys[pg.K_DOWN]): return SOUTH_WEST
    elif (keys[pg.K_d] or keys[pg.K_RIGHT]) and (keys[pg.K_s] or keys[pg.K_DOWN]): return SOUTH_EAST
    elif (keys[pg.K_a] or keys[pg.K_LEFT]): return WEST
    elif (keys[pg.K_d] or keys[pg.K_RIGHT]): return EAST
    elif (keys[pg.K_w] or keys[pg.K_UP]): return NORTH
    elif (keys[pg.K_s] or keys[pg.K_DOWN]): return SOUTH
    else: return IDLE 

def clockToSurfaceFPS(clock: pg.time.Clock, font) -> pg.Surface:
    fps = str(int(clock.get_fps()))
    return font.render(fps, 1, pg.Color("coral"))

if __name__ == "__main__":
    print("All imports working!")