import collections.abc
import abc
import pygame
from pygame import Surface

from APU.entities import Drawable

class Map[T: Drawable](abc.ABC):
    """
    Abstract class that represents a generic map of a game.
    A map is composed by a background surface and a collection of static elements that should be rendered above it.

    This class is supposed to be inherited, and leaves to the concrete classes the implementation of the internal.
    """
    def __init__(self, background: Drawable, *items: T) -> None:
        self.background = background
        self.insert(*items)

    @property
    @abc.abstractmethod
    def static_items(self) -> collections.abc.Iterable[T]:
        """
        Abstract property that returns all the static objects on the map.

        Returns:
            Iterable[T]: An iterable collection of static objects.
        """
        pass

    @abc.abstractmethod
    def insert(self, *items: T) -> None:
        """
        Abstract method to insert static items into the map.

        This method must be implemented in a subclass to define how items are added to
        the collection of static elements of the map.

        Args:
            *items (T): One or more objects to be inserted into the map.
        """
        pass

    @abc.abstractmethod
    def render(self) -> None:
        """
        Renders the map by drawing the background and all the static items onto the provided surface.
        """
        self.background.draw()

newmap = Map(Drawable(pygame.surface.Surface((0,0))))