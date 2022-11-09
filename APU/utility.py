import pygame as pg, time
from typing import Sequence
from APU.core.config import DEFAULT_FPS, KEYMAP

def getSurroundingObjects(object, horizontalDistance = 1, verticalDistance = 1, **kwargs: pg.sprite.Group):
        surroundingObjects = []
        for value in kwargs.values():
            surroundingObjects.extend(
                sprite for sprite in value
                if object.rect.inflate(horizontalDistance, verticalDistance).colliderect(sprite.rect))
        return surroundingObjects

def getDirectionFromKeymap(keys: Sequence[bool]) -> list[int]:
    pressedKeys = [index + 93 for index, value in enumerate(keys) if value]
    return [KEYMAP[key] for key in pressedKeys if key in KEYMAP.keys()]

def clockToSurfaceFPS(clock: pg.time.Clock, font) -> pg.Surface:
    fps = str(int(clock.get_fps()))
    return font.render(fps, 1, pg.Color("coral"))

def clip(surf, x, y, x_size, y_size):
    handle_surf = surf.copy()
    clipR = pg.Rect(x,y,x_size,y_size)
    handle_surf.set_clip(clipR)
    image = surf.subsurface(handle_surf.get_clip())
    return image.copy()

def deltaT(last_time):
    dt = time.time() - last_time
    dt *= DEFAULT_FPS
    updated_last_time = time.time()
    return dt, updated_last_time

def palette_swap(surf, old_c, new_c):
    img_copy = pg.Surface(surf.get_size())
    img_copy.fill(new_c)
    surf.set_colorkey(old_c)
    img_copy.blit(surf, (0, 0))
    return img_copy

if __name__ == "__main__":
    print("All imports working!")