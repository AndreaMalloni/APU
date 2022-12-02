from APU.core.baseSpriteObject import BaseSpriteObject
from APU.core.spritesheet import SpriteStripAnim
import pygame as pg

class AnimatedSpriteObject(BaseSpriteObject):
    """Animated sprite object, inherits from BasicSpriteObject

    Represents a generic animated sprite, providing methods to add an animation sequence 
    and to set which one to play.
    """
    def __init__(self, x:int, y:int, layer:int = 0, defaultSpriteImage:pg.Surface = pg.Surface((0, 0)), defaultSeq:str = None, **kwargs:SpriteStripAnim) -> None:
        """Constructs a sprite object with animation handling functionality.

        Args:
            x (int): x position of the sprite.
            y (int): y position of the sprite.
            layer (int): the layer to draw the image to. Defaults to 0.
            defaultSpriteImage (pg.Surface, optional): the default image to draw. Defaults to pg.Surface((0, 0)) (empty surface).
            defaultSeq (str, optional): default animation sequence to play. Defaults to None.
        """
        super().__init__(x, y, layer, defaultSpriteImage)
        self.animations = {}
        self.currentAnimationSequence = defaultSeq

        if kwargs: self.addAnimationSequence(**kwargs)

    def addAnimationSequence(self, **kwargs:SpriteStripAnim) -> None:
        """Updates the animations dict with any given animation sequence."""
        self.animations.update(**kwargs)
    
    def switchTo(self, animationSeq:str) -> None:
        """Changes the current playing animation and calls the corresponding iter()
        method to start frame iteration

        Args:
            animationSeq (str): the new animation sequence to play

        Raises:
            KeyError: if the given animationSeq does not exist
        """
        if animationSeq is not None and animationSeq not in self.animations.keys():
            raise KeyError(f"This object has no assigned animation sequence for {animationSeq}")

        self.currentAnimationSequence = animationSeq
        if self.currentAnimationSequence is not None: self.animations[self.currentAnimationSequence].iter()
    
    def update(self) -> None:
        """Resets the width and height properties based on the sprite image size and 
        consequently updates the rect, comes in handy when resizing the game window. 
        Overrides the update method of BasicSpriteObject to iterate through all the frames of the current playing sequence.   
        """
        self.width, self.height = self.image.get_size()
        self.rect = pg.rect.Rect(self.x, self.y, self.width, self.height)

        try:
            self.image = self.animations[self.currentAnimationSequence].next()
        except KeyError:
            self.image = self.fallBackImage
