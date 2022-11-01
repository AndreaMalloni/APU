import pygame as pg

class BaseSpriteObject(pg.sprite.Sprite):
    """Basic sprite object

    Represents a generic non-animated sprite and 
    provides methods to draw itself on the (pygame) display and get the current position/size. 
    """
    def __init__(self, x:int, y:int, defaultSpriteImage:pg.Surface = pg.Surface((0, 0))) -> None:
        """Constructs a sprite object with basic functionality.
 
        Args:
            x (int): x position of the sprite.
            y (int): y position of the sprite.
            defaultSpriteImage (pg.Surface, optional): the default image to draw. Defaults to pg.Surface((0, 0)) (empty surface).
        """
        pg.sprite.Sprite.__init__(self)
        self.x = x
        self.y = y
        self.fallBackImage = defaultSpriteImage
        self.image = defaultSpriteImage

        self.width, self.height = self.image.get_size()
        self.rect = pg.rect.Rect(self.x, self.y, self.width, self.height)

    @property
    def position(self) -> tuple[int, int]:
        """Returns a tuple of int values (x position, y position)."""
        return (self.x, self.y)

    @property
    def size(self) -> tuple[int, int]:
        """Returns a tuple of int values (width, height)."""
        return (self.width, self.height)

    def update(self) -> None:
        """Resets the width and height properties based on the sprite image size and 
        consequently updates the rect, comes in handy when resizing the game window.    
        """
        self.width, self.height = self.image.get_size()
        self.rect = pg.rect.Rect(self.x, self.y, self.width, self.height)

    def draw(self, window:pg.display) -> None:
        """Draws the sprite image on the given (pygame) display in the current (x, y) position.

        Args:
            window (pg.display): the display to draw the image to.
        """
        window.blit(self.image, self.position)

if __name__ == "__main__":
    print("All imports working!")

