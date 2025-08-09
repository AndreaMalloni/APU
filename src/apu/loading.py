import json
from pathlib import Path
from typing import Any

import pygame
from typing_extensions import override

from apu.core.spritesheet import SpriteSheet
from apu.entities import BaseSprite

__all__ = ["Loader", "TMXLoader"]


class Loader:
    def load(self, data: Any) -> list[BaseSprite]:
        return []


class TMXLoader(Loader):
    @override
    def load(self, path: str) -> list[BaseSprite]:
        if path.endswith(".json"):
            return self.__load_json(path)
        elif path.endswith(".tmx"):
            return self.__load_tmx(path)
        else:
            raise Exception("Unsupported file format.")

    def __load_json(self, path: str) -> list[BaseSprite]:
        def get_objects(data: dict[str, Any]) -> dict[int, pygame.Rect]:
            objects = {}
            for tileset in data["tilesets"]:
                for tile in tileset["tiles"]:
                    if "objectgroup" in tile:
                        for obj in tile["objectgroup"]["objects"]:
                            objects[tile["id"]] = pygame.rect.Rect(
                                (obj["x"], obj["y"]), (obj["width"], obj["height"])
                            )
            return objects

        def get_images(data: dict[str, Any], sheet: SpriteSheet) -> dict[int, pygame.Surface]:
            images = {}
            tile_size = (data["tilewidth"], data["tileheight"])

            for layer in data["layers"]:
                for tile_id in layer["data"]:
                    if isinstance(tile_id, int):
                        image_position = divmod(
                            tile_id - 1, sheet.sheet.get_size()[0] // tile_size[0]
                        )
                        image_position = (
                            image_position[1] * tile_size[0],
                            image_position[0] * tile_size[1],
                        )

                        image = sheet.image_at(
                            pygame.rect.Rect(image_position, (tile_size[0], tile_size[1]))
                        )
                        image.set_colorkey((0, 0, 0))
                        images[tile_id - 1] = image
            return images

        with Path(path).open() as f:
            json.load(f)

        sprites: list[BaseSprite] = []

        """
        for layer_index, layer in enumerate(json_data["layers"]):
            for tile_index, tile_id in enumerate(layer["data"]):
                if tile_id != 0:
                    tile_position = divmod(tile_index, json_data["width"])
                    tile_position = (tile_position[1] * tile_size[1], 
                                   tile_position[0] * tile_size[0])

                    # tile animations

                    sprite = APU.entities.BaseSprite(position=tile_position,
                                                     layer=layer_index,
                                                     image=images[tile_id - 1])
                    if tile_id - 1 in objects:
                        sprite.add_hitbox(box1=objects[tile_id - 1])
                    sprites.append(sprite)
        """
        return sprites

    def __load_tmx(self, path: str) -> list[BaseSprite]:
        return []


if __name__ == "__main__":
    TMXLoader().load("C:\\Users\\mallo\\Documents\\GitHub\\APU\\assets\\map.json")
