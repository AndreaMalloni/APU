from APU.core.config import IDLE, NORTH, EAST, SOUTH, WEST
from APU.core.animatedSpriteObject import AnimatedSpriteObject
import pygame as pg

class MovingObject(AnimatedSpriteObject):
    def __init__(self, x:int, y:int, layer:int = 0, defaultSpriteImage = None, speed = 1, **kwargs):
        super().__init__(x, y, layer, defaultSpriteImage, **kwargs)
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

    def move(self, directions:list[int], dt:float = 1, lookFor:list[pg.Rect] = None):
        if directions: 
            self.isMoving = True
            self.facingDirection = directions[0]
            self.movingDirection = directions[0]
            
            if lookFor: 
                collidingDirections = self._checkCollisions(lookFor)
                for direction in collidingDirections:
                    if direction in directions: directions.remove(direction)
            for direction in directions:
                self._movements[direction](dt)
        else:
            self.isMoving = False
            self.movingDirection = IDLE

    def _checkCollisions(self, lookFor:list[pg.Rect]):
        collidingDirections = []
        colliding = self.rect.collidelistall(lookFor)
        for index in colliding:
            rect = lookFor[index]
            if ((rect.bottomleft[0] <= self.rect.midtop[0] <= rect.bottomright[0]) and 
                (rect.bottomleft[1] >= self.rect.midtop[1] <= rect.bottomright[1]) and 
                rect.centery <= self.rect.centery):
                collidingDirections.append(NORTH)
            if ((rect.topleft[0] <= self.rect.midbottom[0] <= rect.topright[0]) and 
                (rect.topleft[1] <= self.rect.midbottom[1] >= rect.topright[1]) and 
                rect.centery >= self.rect.centery):
                collidingDirections.append(SOUTH)
            if ((rect.topright[1] <= self.rect.midleft[1] <= rect.bottomright[1]) and 
                (rect.topright[0] >= self.rect.midleft[0] <= rect.bottomleft[0]) and 
                rect.centerx <= self.rect.centerx):
                collidingDirections.append(WEST)
            if ((rect.topleft[1] <= self.rect.midright[1] <= rect.bottomleft[1]) and 
                (rect.topleft[0] <= self.rect.midright[0] >= rect.bottomleft[0]) and 
                rect.centerx >= self.rect.centerx):
                collidingDirections.append(EAST)

        return collidingDirections  

    def _moveNorth(self, dt):
        self.y -= self.speed * dt

    def _moveEast(self, dt):
        self.x += self.speed * dt

    def _moveSouth(self, dt):
        self.y += self.speed * dt

    def _moveWest(self, dt):
        self.x -= self.speed * dt

if __name__ == "__main__":
    print("All imports working!")