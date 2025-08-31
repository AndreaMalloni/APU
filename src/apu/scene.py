from abc import ABC, abstractmethod
from collections.abc import Callable, Iterator
from typing import Generic, TypeVar

import pygame
from typing_extensions import override

from apu.core.enums import NEIGHBOUR_MATRIX
from apu.objects.components import MovementComponent
from apu.objects.entities import BaseSprite

__all__ = ["Scene", "TiledScene"]

T = TypeVar("T")


class Scene(ABC, Generic[T]):
    @abstractmethod
    def insert(self, *items: T) -> None: ...

    @abstractmethod
    def remove(self, *items: T) -> None: ...

    @abstractmethod
    def render(self, window: pygame.Surface) -> None: ...

    @abstractmethod
    def update(self) -> None: ...

    @abstractmethod
    def has(self, item: T) -> bool: ...

    @abstractmethod
    def find(self, predicate: Callable[[T], bool]) -> Iterator[T]: ...

    @abstractmethod
    def on_enter(self) -> None: ...

    @abstractmethod
    def on_exit(self) -> None: ...

    @abstractmethod
    def __iter__(self) -> Iterator[T]: ...


class TiledScene(Scene[BaseSprite]):
    def __init__(self, tile_size: int, *items: BaseSprite) -> None:
        self.static_items: dict[int, dict[tuple[int, int], BaseSprite]] = {}
        self.dynamic_items: pygame.sprite.Group[BaseSprite] = pygame.sprite.Group()
        self.tile_size = tile_size
        self.insert(*items)

    @override
    def insert(self, *items: BaseSprite) -> None:
        for item in items:
            if item.get_component(MovementComponent) is None:
                if item.layer not in self.static_items:
                    self.static_items[item.layer] = {}
                self.static_items[item.layer][item.position] = item
            else:
                self.dynamic_items.add(item)

    @override
    def remove(self, *items: BaseSprite) -> None:
        for item in items:
            if item.get_component(MovementComponent) is None:
                if item.layer in self.static_items:
                    self.static_items[item.layer].pop(item.position, None)
            else:
                self.dynamic_items.remove(item)

    @override
    def render(self, window: pygame.surface.Surface) -> None:
        all_layers = sorted(self.static_items.keys())
        for item in self.dynamic_items:
            if item._layer not in all_layers:
                all_layers.append(item._layer)

        all_layers.sort()

        for layer in all_layers:
            if layer in self.static_items:
                for item in self.static_items[layer].values():
                    item.draw(window)

            for item in self.dynamic_items:
                if item._layer == layer:
                    item.draw(window)

    @override
    def update(self) -> None:
        self.dynamic_items.update()

        for layer in self.static_items:
            for position in self.static_items[layer]:
                self.static_items[layer][position].update()

    @override
    def has(self, item: BaseSprite) -> bool:
        return (
            item.layer in self.static_items
            and item.position in self.static_items[item.layer]
            and self.static_items[item.layer][item.position] is item
        )

    @override
    def find(self, predicate: Callable[[BaseSprite], bool]) -> Iterator[BaseSprite]:
        for sprite in self.dynamic_items:
            if predicate(sprite):
                yield sprite

        for layer in sorted(self.static_items.keys()):
            for sprite in self.static_items[layer].values():
                if predicate(sprite):
                    yield sprite

    @override
    def on_enter(self) -> None:
        self.active = True

    @override
    def on_exit(self) -> None:
        self.active = False

    def neighbours(self, item: BaseSprite) -> list[BaseSprite]:
        position = item.position
        layer = item.layer
        neighbour_tiles = []

        for offset in NEIGHBOUR_MATRIX:
            neighbour_position = (
                position[0] + offset[0] * self.tile_size,
                position[1] + offset[1] * self.tile_size,
            )
            if neighbour_position in self.static_items[layer]:
                neighbour_tiles.append(self.static_items[layer][neighbour_position])
        return neighbour_tiles

    @override
    def __iter__(self) -> Iterator[BaseSprite]:
        for layer in sorted(self.static_items.keys()):
            yield from self.static_items[layer].values()

        yield from self.dynamic_items

    @override
    def __str__(self) -> str:
        total_sprites = len(list(self))
        return f"""
        Scene: {super().__str__()}
        Tile size: {self.tile_size}
        Number of static_items = {total_sprites}
        """
