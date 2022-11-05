from APU.movingObject import MovingObject
from APU.core.spritesheet import SpriteStripAnim
import pygame as pg

class EntityObject(MovingObject):
    def __init__(self, x:int, y:int, defaultSpriteImage:pg.Surface = pg.Surface((0, 0)), speed = 1.0, hp = 10, **kwargs:SpriteStripAnim):
        super().__init__(x, y, defaultSpriteImage, speed, **kwargs)
        self.hp = hp

    def damaged(self, damage:int):
        self.hp -= damage

if __name__ == "__main__":
    print("All imports working!")
