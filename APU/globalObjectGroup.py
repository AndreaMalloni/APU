import pygame as pg

class GlobalObjectGroup(pg.sprite.RenderUpdates):
    def __init__(self):
        super().__init__()

    def update(self):
        for sprite in self.sprites():
            sprite.update()

if __name__ == "__main__":
    print("All imports working!")