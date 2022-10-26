from APU.core.baseSpriteObject import BaseSpriteObject
from APU.core.spritesheet import SpriteStripAnim

class AnimatedSpriteObject(BaseSpriteObject):
    def __init__(self, x: int, y: int, defaultSpriteImage = None, **kwargs: SpriteStripAnim) -> None:
        super().__init__(x, y, defaultSpriteImage)
        self.animations = {}
        self.currentAnimationSequence = None

        self.addAnimationSequence(**kwargs)

    def addAnimationSequence(self, **kwargs):
        for key in kwargs:
            self.animations[key] = kwargs[key]
        
        #self.currentAnimationSequence = kwargs.keys()[0]
    
    def switchTo(self, animationKey):
        if animationKey not in self.animations.keys():
            raise Exception(f"This object has no assigned animation sequence for {animationKey}")

        self.currentAnimationSequence = animationKey
        self.animations[self.currentAnimationSequence].iter()
    
    def draw(self, window):
        try:
            self.image = self.animations[self.currentAnimationSequence].next()
        except KeyError:
            self.image = self._defaultSpriteImage
        window.blit(self.image, (self.x, self.y))
