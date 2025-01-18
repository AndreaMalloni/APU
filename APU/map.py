import collections.abc
import abc
import pygame
from pygame import Surface

from APU.entities import Drawable, BaseSprite


class Map[T: Drawable, E: collections.abc.Collection](abc.ABC):
    """
    Abstract class that represents a generic map of a game.
    A map is composed by a background surface and a collection of static elements that should be rendered above it.

    This class is supposed to be inherited, and leaves to the concrete classes the implementation of the internal logic
    and data structure.
    """
    def __init__(self, background: Drawable, *items: T) -> None:
        self.background: Drawable = background
        self.insert(*items)

    @property
    @abc.abstractmethod
    def static_items(self) -> E:
        """
        Abstract property that returns all the static objects on the map.

        Returns:
            E: A collection of static objects.
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
    def render(self, destination: pygame.surface.Surface) -> None:
        """
        Renders the map by drawing the background and all the static items onto the provided surface.

        Args:
            destination (pygame.surface.Surface): The surface where the map must be rendered.
        """
        self.background.draw(destination)


class TiledMap(Map[BaseSprite, dict[int, dict[tuple, BaseSprite]]]):
    def __init__(self, tile_size: tuple[int, int], background: Drawable, *items: BaseSprite):
        self._static_items: dict[int, dict[tuple, BaseSprite]] = {}
        self.tile_size: tuple[int, int] = tile_size
        super().__init__(background, *items)

    @property
    def static_items(self) -> dict[int, dict[tuple, BaseSprite]]:
        return self._static_items

    def insert(self, *items: BaseSprite) -> None:
        self._static_items.update({item.layer: {item.position: item} for item in items} )

    def render(self, destination: pygame.surface.Surface) -> None:
        super().render(destination)
        for layer in self.static_items:
            for position in self.static_items[layer]:
                self.static_items[layer][position].draw(destination)
