import pygame as pg

class BaseSpriteObject(pg.sprite.Sprite):
    def __init__(self, x:int, y:int, defaultSpriteImage = None) -> None:
        pg.sprite.Sprite.__init__(self)
        self.x = x
        self.y = y
        self._defaultSpriteImage = defaultSpriteImage
        self.image = defaultSpriteImage

        if self.image is None:  self.width, self.height = 0, 0
        else:   self.width, self.height = self.image.get_size()

        self.rect = pg.rect.Rect(self.x, self.y, self.width, self.height)

    @property
    def position(self) -> tuple[int, int]:
        return (self.x, self.y)

    @property
    def size(self) -> tuple[int, int]:
        return (self.width, self.height)

    def update(self) -> None:
        self.width, self.height = self.image.get_size()
        self.rect = pg.rect.Rect(self.x, self.y, self.width, self.height)

    def collide(self, spriteObject):
        pass

    def draw(self, window) -> None:
        window.blit(self.image, (self.x, self.y))

if __name__ == "__main__":
    print("All imports working!")

