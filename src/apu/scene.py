from collections.abc import Iterator
from typing import Any

import pygame
from typing_extensions import override

from apu.core.enums import NEIGHBOUR_MATRIX
from apu.entities import BaseSprite


class Scene:
    def insert(self, *items: Any) -> None:
        pass

    def render(self, window: pygame.Surface) -> None:
        pass

    def update(self) -> None:
        pass

    def neighbours(self, item: Any) -> list[Any]:
        return []

    def __iter__(self) -> Iterator[Any]:
        return self

    def __next__(self) -> Any:
        raise StopIteration


class TiledScene(Scene):
    def __init__(self, tile_size: int, *items: BaseSprite) -> None:
        self.tiles: dict[int, dict[tuple[int, int], BaseSprite]] = {}
        self.tile_size = tile_size
        self.show_hitbox = False
        self.insert(*items)

        self.__current_layer = 0
        self.__current_position = 0

    @override
    def insert(self, *items: BaseSprite) -> None:
        for tile in items:
            if tile.layer not in self.tiles:
                self.tiles[tile.layer] = {}
            self.tiles[tile.layer][tile.position] = tile

    @override
    def render(self, window: pygame.surface.Surface, offset: tuple[int, int] = (0, 0)) -> None:
        for layer in self.tiles:
            for position in self.tiles[layer]:
                self.tiles[layer][position].draw(window)

                if self.show_hitbox:
                    for hitbox in self.tiles[layer][position].hitboxes.values():
                        pygame.draw.rect(window, (255, 0, 0), hitbox, width=1)

    @override
    def update(self, offset: tuple[int, int] = (0, 0)) -> None:
        pass

    @override
    def neighbours(self, item: BaseSprite) -> list[BaseSprite]:
        position = item.position
        layer = item.layer
        neighbour_tiles = []

        for offset in NEIGHBOUR_MATRIX:
            neighbour_position = (
                position[0] + offset[0] * self.tile_size,
                position[1] + offset[1] * self.tile_size,
            )
            if neighbour_position in self.tiles[layer]:
                neighbour_tiles.append(self.tiles[layer][neighbour_position])
        return neighbour_tiles

    @override
    def __iter__(self) -> Iterator[BaseSprite]:
        return self

    @override
    def __next__(self) -> BaseSprite:
        current_layer = list(self.tiles.keys())[self.__current_layer]

        if self.__current_layer < len(self.tiles) - 1:
            self.__current_layer += 1
        else:
            self.__current_layer = 0
            self.__current_position += 1

        if self.__current_position >= len(self.tiles[current_layer]):
            raise StopIteration

        current_position = list(self.tiles[current_layer].keys())[self.__current_position]
        current_sprite = self.tiles[current_layer][current_position]

        return current_sprite
