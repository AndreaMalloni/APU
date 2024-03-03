import pygame

from APU.entities import BaseSprite

NEIGHBOUR_MATRIX = [(-1, 0), (-1, -1), (0, -1), (1, -1), (1, 0), (1, 1), (0, 1), (-1, 1)]


class Scene:
    def insert(self, *items):
        pass

    def render(self, window):
        pass

    def update(self):
        pass

    def neighbours(self, item):
        pass

    def __iter__(self):
        return self

    def __next__(self):
        pass


class TiledScene(Scene):
    def __init__(self, tile_size, *items: BaseSprite) -> None:
        self.tiles = {}
        self.tile_size = tile_size
        self.show_hitbox = False
        self.insert(*items)

        self.__current_layer = 0
        self.__current_position = 0

    def insert(self, *items: BaseSprite):
        for tile in items:
            if tile.layer not in self.tiles.keys():
                self.tiles[tile.layer] = {}
            self.tiles[tile.layer][tile.position] = tile

    def render(self, window: pygame.surface.Surface, offset: tuple[int, int] = (0, 0)) -> None:
        for layer in self.tiles:
            for position in self.tiles[layer]:
                self.tiles[layer][position].draw(window)

                if self.show_hitbox:
                    for hitbox in self.tiles[layer][position].hitboxes.values():
                        pygame.draw.rect(window, (255, 0, 0), hitbox, width=1)

    def update(self, offset: tuple[int, int] = (0, 0)):
        pass

    def neighbours(self, item: BaseSprite) -> list[BaseSprite]:
        position = item.position
        layer = item.layer
        neighbour_tiles = []

        for offset in NEIGHBOUR_MATRIX:
            neghbour_position = (position[0] + offset[0] * self.tile_size, position[1] + offset[1] * self.tile_size)
            if self.tiles[layer][neghbour_position]:
                neighbour_tiles.append(self.tiles[layer][neghbour_position])
        return neighbour_tiles

    def __iter__(self):
        return self

    def __next__(self):
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

