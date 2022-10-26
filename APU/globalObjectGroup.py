import pygame as pg

class GlobalObjectGroup(pg.sprite.Group):
    def __init__(self):
        super().__init__()

    def update(self):
        for sprite in self.sprites():
            sprite.update()

    def draw(self, window):
        for sprite in self.sprites():
            sprite.draw(window)

if __name__ == "__main__":
    print("All imports working!")