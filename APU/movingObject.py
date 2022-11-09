from APU.core.config import IDLE, NORTH, EAST, SOUTH, WEST
from APU.core.animatedSpriteObject import AnimatedSpriteObject
import pygame as pg

class MovingObject(AnimatedSpriteObject):
    def __init__(self, x:int, y:int, defaultSpriteImage = None, speed = 1, **kwargs):
        super().__init__(x, y, defaultSpriteImage, **kwargs)
        self.speed = speed
        self.isMoving = False
        self.movingDirection = IDLE
        self.facingDirection = SOUTH

        self._movements = {
            NORTH: self._moveNorth,
            EAST: self._moveEast,
            SOUTH: self._moveSouth,
            WEST: self._moveWest,
        }

    def move(self, directions:list[int], dt = 1):
        self.isMoving = IDLE not in directions
        self.movingDirection = directions[0] if directions else IDLE

        if IDLE not in directions: 
            if directions: self.facingDirection = directions[0]
            for direction in directions:
                self._movements[direction](dt)

    def _moveNorth(self, dt):
        self.y -= self.speed * dt

    def _moveEast(self, dt):
        self.x += self.speed * dt

    def _moveSouth(self, dt):
        self.y += self.speed * dt

    def _moveWest(self, dt):
        self.x -= self.speed * dt

    def predictDirectionalCollision(self):
        #HINT check x & y axis individually
        return False

if __name__ == "__main__":
    print("All imports working!")