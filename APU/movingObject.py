from APU.core.config import IDLE, NORTH, NORTH_EAST, EAST, SOUTH_EAST, SOUTH, SOUTH_WEST, WEST, NORTH_WEST
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
            NORTH_EAST: self._moveNorthEast,
            EAST: self._moveEast,
            SOUTH_EAST: self._moveSouthEast,
            SOUTH: self._moveSouth,
            SOUTH_WEST: self._moveSouthWest,
            WEST: self._moveWest,
            NORTH_WEST: self._moveNorthWest,
        }

    def move(self, direction:int, dt = 1):
        self.isMoving = direction != IDLE
        self.movingDirection = direction

        if direction != IDLE: 
            self.facingDirection = direction
            self._movements[direction](dt)

    def _moveNorth(self, dt):
        self.y -= self.speed * dt

    def _moveNorthEast(self, dt):
        self.x += self.speed * dt
        self.y -= self.speed * dt

    def _moveEast(self, dt):
        self.x += self.speed * dt

    def _moveSouthEast(self, dt):
        self.x += self.speed * dt
        self.y += self.speed * dt

    def _moveSouth(self, dt):
        self.y += self.speed * dt

    def _moveSouthWest(self, dt):
        self.x -= self.speed * dt
        self.y += self.speed * dt

    def _moveWest(self, dt):
        self.x -= self.speed * dt

    def _moveNorthWest(self, dt):
       self.x -= self.speed * dt
       self.y -= self.speed * dt

    def predictDirectionalCollision(self):
        #HINT check x & y axis individually
        return False

if __name__ == "__main__":
    print("All imports working!")