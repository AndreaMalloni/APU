from __future__ import annotations

import os
from copy import copy
from time import perf_counter
from typing import Iterable

import pygame


class SpriteSheet:
    """Sprite sheet

    Represents a sprite sheet object, providing methods to access sprite images directly or extract
    multiple sprites simultaneously. 
    """

    def __init__(self, path: str) -> None:
        """Constructs a sprite sheet object, loading an image from the given path.

        Args:
            path (str): sprite sheet path.

        Raises:
            FileNotFoundError: if the given sprite sheet file does not exist.
        """
        if not os.path.exists(path):
            raise FileNotFoundError(f"File not found: {path}")

        self.sheet = pygame.image.load(path).convert()

    def image_at(self, rect: pygame.Rect, color_key: pygame.Color = None) -> pygame.Surface:
        """Returns a specific sprite surface from the sprite sheet, given its rect area.

        Args:
            rect (pygame.Rect): rect area of the wanted image.
            color_key (pygame.Color, optional): background color, transparency is applied. Defaults to None.

        Returns:
            pygame.Surface: a (pygame) surface.
        """
        rect = pygame.Rect(rect)
        image = pygame.Surface(rect.size).convert()
        image.blit(self.sheet, (0, 0), rect)

        if color_key is not None:
            image.set_colorkey(color_key, pygame.RLEACCEL)
        return image

    def images_at(self, rects: list[pygame.Rect], color_key: pygame.Color = None) -> list[pygame.Surface]:
        """Returns a list of sprite surfaces from the sprite sheet, given their rect areas.

        Args:
            rects (Iterable[pygame.Rect]): list of rect areas of the wanted images.
            color_key (pygame.Color, optional): background color, transparency is applied. Defaults to None.

        Returns:
            list[pygame.Surface]: a list of (pygame) surfaces.
        """
        return [self.image_at(rect, color_key) for rect in rects]

    def load_sequence(self, rect: pygame.Rect, image_count: int, color_key: pygame.Color = None) -> list[pygame.Surface]:
        """Returns a strip of consecutive images, given the starting rect area 
        and the number of images to return.

        Args:
            rect (pygame.Rect): rect area of the starting image.
            image_count (int): number of images per strip.
            color_key (pygame.Color, optional): background color, transparency is applied. Defaults to None.

        Returns:
            list[pygame.Surface]: a list of (pygame) surfaces.
        """
        rects = [pygame.Rect(rect[0] + rect[2] * x, rect[1], rect[2], rect[3]) for x in range(image_count)]
        return self.images_at(rects, color_key)


class AnimationSequence:
    """Sprite strip animator
    
    This class represents a sprite animation sequence and provides 
    an iterator (iter() and next() methods), and a __add__() method for joining strips.
    """

    def __init__(self, frames: list[pygame.surface.Surface], loop: bool = False, frame_duration: float = 0) -> None:
        """Constructs a SpriteStripAnimation

        Args:
            frames: a sequence of images.
            loop: when True, next() method will loop. If False, raises StopIteration when the animation ends.
            frame_duration: ms of duration, same image will be returned before advancing to the next one.
        """
        self.frames = frames
        self.loop = loop
        self.frame_duration = frame_duration
        self.running = True

        self.__current_frame = 0
        self.__start_time = 0

    def mirror(self, flip_x: bool = True, flip_y: bool = False):
        animation = copy(self)
        animation.frames = [pygame.transform.flip(image, flip_x, flip_y) for image in animation.frames]
        return animation

    def __iter__(self) -> object:
        """Starts an iteration"""
        self.__current_frame = 0
        self.__start_time = perf_counter()
        return self

    def __next__(self) -> pygame.Surface:
        if self.running:
            if self.__current_frame >= len(self.frames):
                if self.loop:
                    self.__current_frame = 0
                else:
                    raise StopIteration

            image = self.frames[self.__current_frame]

            current_time = perf_counter()
            if (current_time - self.__start_time) * 1000 >= self.frame_duration:
                self.__current_frame += 1
                self.__start_time = perf_counter()
        else:
            image = self.frames[self.__current_frame]

        return image

    def __add__(self, sequence: AnimationSequence):
        self.frames.extend(sequence.frames)
        return self
