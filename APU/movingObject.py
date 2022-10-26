from APU.core.config import IDLE, NORTH, NORTH_EAST, EAST, SOUTH_EAST, SOUTH, SOUTH_WEST, WEST, NORTH_WEST
from APU.core.animatedSpriteObject import AnimatedSpriteObject
import pygame as pg

class MovingObject(AnimatedSpriteObject):
    def __init__(self, x:int, y:int, defaultSpriteImage = None, speed = 1.0, **kwargs):
        super().__init__(x, y, defaultSpriteImage, **kwargs)
        self.speed = speed
        self.isMoving = False
        self.movingDirection = IDLE
        self.facingDirection = SOUTH

        self.movements = {
            NORTH: [lambda: self.x, lambda: self.y - self.speed],
            NORTH_EAST: [lambda: self.x + self.speed, lambda: self.y - self.speed],
            EAST: [lambda: self.x + self.speed, lambda: self.y],
            SOUTH_EAST: [lambda: self.x + self.speed, lambda: self.y + self.speed],
            SOUTH: [lambda: self.x, lambda: self.y + self.speed],
            SOUTH_WEST: [lambda: self.x - self.speed, lambda: self.y + self.speed],
            WEST: [lambda: self.x - self.speed, lambda: self.y],
            NORTH_WEST: [lambda: self.x - self.speed, lambda: self.y - self.speed],
            IDLE: [lambda: self.x, lambda: self.y]
        }

    def move(self, direction:int):
        self.isMoving = direction != IDLE
        self.movingDirection = direction
        if direction != IDLE: self.facingDirection = direction

        self.x = self.movements[direction][0]()
        self.y = self.movements[direction][1]()

    def predictDirectionalCollision(self):
        #HINT check x & y axis individually
        return False

if __name__ == "__main__":
    print("All imports working!")