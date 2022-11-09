import pygame as pg
from typing import Iterable
import os

class Spritesheet(object):
    """Spritesheet

    Represents a spritesheet object, providing methods to access sprite images directly or extract 
    multiple sprites simultaneously. 
    """
    def __init__(self, path:str) -> None:
        """Constructs a spritesheet object, loading an image from the given path.

        Args:
            path (str): spritesheet path.

        Raises:
            FileNotFoundError: if the given spritesheet file does not exist.
        """
        if not os.path.exists(path): 
            raise FileNotFoundError(f"Font file not found: {path}")
        
        self.sheet = pg.image.load(path).convert()

    def image_at(self, rect:pg.Rect, colorkey:pg.Color = None) -> pg.Surface:
        """Returns a specific sprite surface from the spritesheet, given its rect area.

        Args:
            rect (pg.Rect): rect area of the wanted image.
            colorkey (pg.Color, optional): background color, transparency is applied. Defaults to None.

        Returns:
            pg.Surface: a (pygame) surface.
        """
        rect = pg.Rect(rect)
        image = pg.Surface(rect.size).convert()
        image.blit(self.sheet, (0, 0), rect)

        if colorkey is not None: image.set_colorkey(colorkey, pg.RLEACCEL)
        return image

    def images_at(self, rects:Iterable[pg.Rect], colorkey:pg.Color = None) -> list[pg.Surface]:
        """Returns a list of sprite surfaces from the spritesheet, given their rect areas.

        Args:
            rects (Iterable[pg.Rect]): list of rect areas of the wanted images.
            colorkey (pg.Color, optional): background color, transparency is applied. Defaults to None.

        Returns:
            list[pg.Surface]: a list of (pygame) surfaces.
        """
        return [self.image_at(rect, colorkey) for rect in rects]

    def load_strip(self, rect:pg.Rect, image_count:int, colorkey:pg.Color = None) -> list[pg.Surface]:
        """Returns a strip of consecutive images, given the starting rect area 
        and the number of images to return.

        Args:
            rect (pg.Rect): rect area of the starting image.
            image_count (int): number of images per strip.
            colorkey (pg.Color, optional): background color, transparency is applied. Defaults to None.

        Returns:
            list[pg.Surface]: a list of (pygame) surfaces.
        """
        rects = [(rect[0] + rect[2]*x, rect[1], rect[2], rect[3]) for x in range(image_count)]
        return self.images_at(rects, colorkey)


class SpriteStripAnim(object):
    """Sprite strip animator
    
    This class represents a sprite animation sequence and provides 
    an iterator (iter() and next() methods), and a __add__() method for joining strips.
    """
    def __init__(self, path:str, rect:pg.Rect, image_count:int, colorkey:pg.Color = None, loop:bool = False, ticks:int = 1) -> None:
        """Constructs a SpriteStripAnim

        Args:
            rect (pg.Rect): rect area of the starting image.
            image_count (int): number of images per strip.
            colorkey (pg.Color, optional): background color, transparency is applied. Defaults to None.
            loop: when True, next() method will loop. If False, raises StopIteration when the animation ends.
            ticks: number of ticks (ms) to return the same image before advancing to the next image.
        """
        
        self.path = path
        self.images = Spritesheet(path).load_strip(rect, image_count, colorkey)
        self.currentFrame = 0
        self.loop = loop
        self.ticks = ticks
        self._countdown = ticks

    def iter(self) -> object:
        """Starts an iteration"""
        self.currentFrame = 0
        self._countdown = self.ticks
        return self
        
    def next(self) -> pg.Surface:
        if self.currentFrame >= len(self.images):
            if self.loop: self.currentFrame = 0
            else: raise StopIteration
                
        image = self.images[self.currentFrame]

        self._countdown -= 1
        if self._countdown == 0:
            self.currentFrame += 1
            self._countdown = self.ticks
        return image

    def __add__(self, ss:Spritesheet) -> object:
        self.images.extend(ss.images)
        return self