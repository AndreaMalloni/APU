import pygame as pg
from APU.movingObject import MovingObject

class CameraGroup(pg.sprite.LayeredUpdates):
    def __init__(self, cameraX:int, cameraY:int, cameraSize:tuple[int, int]):
        super().__init__()
        self.x = cameraX
        self.y = cameraY
        self.size = cameraSize
        self.mode = 0
        self.followObject = None
        self.renderList = pg.sprite.LayeredUpdates()

    def customDraw(self, window):
        self.renderList.draw(window)

    def customUpdate(self):
        if self.followObject is not None and self.followObject.isMoving:
            self.centerPosition()

            for sprite in self.sprites():
                sprite.x = sprite.x - self.x
                sprite.y = sprite.y - self.y
                
                if (self.x < sprite.x < self.size[0] or self.x < sprite.x + sprite.size[0] < self.size[0]) and (self.y < sprite.y < self.size[1] or self.y < sprite.y + sprite.size[1] < self.size[1]):
                    self.renderList.add(sprite)
                elif sprite in self.renderList:
                    self.renderList.remove(sprite)
        self.update()

    def setMode(self, mode:int, followObject:MovingObject = None):
        self.followObject = followObject

    def centerPosition(self):
        self.x = self.followObject.x + self.followObject.size[0]/2 - self.size[0]/2
        self.y = self.followObject.y + self.followObject.size[1]/2 - self.size[1]/2

if __name__ == "__main__":
    print("All imports working!")