from APU.movingObject import MovingObject
import pygame as pg

class EntityObject(MovingObject):
    def __init__(self, x:int, y:int, defaultSpriteImage = None, speed = 1.0, hp = 10, **kwargs):
        super().__init__(x, y, defaultSpriteImage, speed, **kwargs)
        self.hp = hp

    def damaged(self, damage:int):
        self.hp -= damage

if __name__ == "__main__":
    print("All imports working!")
