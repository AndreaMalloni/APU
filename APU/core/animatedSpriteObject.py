from argparse import ArgumentError
from email.policy import strict
from APU.core.baseSpriteObject import BaseSpriteObject
from APU.core.spritesheet import SpriteStripAnim

class AnimatedSpriteObject(BaseSpriteObject):
    def __init__(self, x: int, y: int, defaultSpriteImage = None, **kwargs: SpriteStripAnim) -> None:
        super().__init__(x, y, defaultSpriteImage)
        self.animations = {}
        self.currentAnimationSequence = None
        self.currentFrame = 0

        self.addAnimationSequence(**kwargs)

    def addAnimationSequence(self, **kwargs):
        for key in kwargs:
            self.animations[key] = kwargs[key]
    
    def switchTo(self, animationKey):
        if animationKey not in self.animations.keys():
            raise ArgumentError(f"This object has no assigned animation sequence for {animationKey}")

        self.currentAnimationSequence = animationKey
        self.currentFrame = 0

    