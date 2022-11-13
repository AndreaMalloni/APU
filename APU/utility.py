import pygame as pg 
from time import perf_counter
from APU.core.baseSpriteObject import BaseSpriteObject

def getSurroundingObjects(object:BaseSpriteObject, horizontalDistance:int = 1, verticalDistance:int = 1, **kwargs:pg.sprite.Group) -> list[BaseSpriteObject]:
    surroundingObjects = []
    for value in kwargs.values():
        surroundingObjects.extend(
            sprite for sprite in value
            if object.rect.inflate(horizontalDistance, verticalDistance).colliderect(sprite.rect))
    return surroundingObjects

def clockToSurfaceFPS(clock:pg.time.Clock, font:pg.font.Font) -> pg.Surface:
    fps = str(int(clock.get_fps()))
    return font.render(fps, 1, pg.Color("coral"))

def clip(surf:pg.Surface, x:int, y:int, width:int, heigth:int) -> pg.Surface:
    handle_surf = surf.copy()
    rect = pg.Rect(x, y, width, heigth)
    handle_surf.set_clip(rect)
    image = surf.subsurface(handle_surf.get_clip())
    return image.copy()

def deltaT(last_time:float) -> tuple[float, float]:
    dt = perf_counter() - last_time
    dt *= 60
    updated_last_time = perf_counter()
    return dt, updated_last_time

def palette_swap(surf:pg.Surface, oldColor:pg.Color, newColor:pg.Color) -> pg.Surface:
    imgCopy = pg.Surface(surf.get_size())
    imgCopy.fill(newColor)
    surf.set_colorkey(oldColor)
    imgCopy.blit(surf, (0, 0))
    return imgCopy

if __name__ == "__main__":
    print("All imports working!")