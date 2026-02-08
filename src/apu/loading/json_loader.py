import json
from pathlib import Path
from typing import Any

import pygame
from typing_extensions import override

from apu.collision import HitBox
from apu.core.spritesheet import AnimationSequence, SpriteSheet
from apu.loading.loader_base import MapLoader
from apu.objects.components import AnimationComponent, SolidBodyComponent
from apu.objects.entities import BaseSprite

__all__ = ["JSONMapLoader"]


class JSONMapLoader(MapLoader):
    """Loader for Tiled maps in JSON format."""

    @override
    def supports_format(self, file_path: str) -> bool:
        return file_path.lower().endswith(".json")

    @override
    def load(self, map_path: str, assets_path: str) -> list[BaseSprite]:
        """Loads a Tiled map from JSON file.

        Args:
            map_path: Path to the JSON map file
            assets_path: Path to the assets directory

        Returns:
            List of BaseSprite representing the map elements
        """
        with Path(map_path).open() as f:
            json_data = json.load(f)

        tile_size = json_data["tileheight"]
        tileset_path = self._get_tileset_path(json_data, assets_path)
        sheet = SpriteSheet(tileset_path)

        hitboxes = self._load_objects(json_data)

        animations = self._load_animations(json_data, sheet, tile_size)

        sprites = []
        for layer_index, layer in enumerate(json_data["layers"]):
            if layer["type"] == "tilelayer":
                layer_sprites = self._create_layer_sprites(
                    layer, json_data, sheet, tile_size, layer_index, hitboxes, animations
                )
                sprites.extend(layer_sprites)

        return sprites

    def _get_tileset_path(self, json_data: dict[str, Any], assets_path: str) -> str:
        """Extracts the tileset path from JSON.

        Args:
            json_data: JSON data of the map
            assets_path: Base path of assets

        Returns:
            Complete path to the tileset file
        """
        tileset = json_data["tilesets"][0]
        return str(assets_path + tileset["image"])

    def _load_objects(self, json_data: dict[str, Any]) -> dict[int, HitBox]:
        """Loads object information (hitboxes) from JSON.

        Args:
            json_data: JSON data of the map

        Returns:
            Dictionary mapping tile ID -> pygame.Rect for hitboxes
        """
        objects = {}
        for tileset in json_data["tilesets"]:
            firstgid = tileset["firstgid"]
            for tile in tileset.get("tiles", []):
                if "objectgroup" in tile:
                    for obj in tile["objectgroup"]["objects"]:
                        objects[firstgid + tile["id"]] = HitBox(
                            pygame.Rect((obj["x"], obj["y"]), (obj["width"], obj["height"]))
                        )
        return objects

    def _load_animations(
        self, json_data: dict[str, Any], sheet: SpriteSheet, tile_size: int
    ) -> dict[int, list[AnimationSequence]]:
        """Loads animation information from JSON.

        Args:
            json_data: JSON data of the map
            sheet: SpriteSheet of the tileset
            tile_size: Size of tiles

        Returns:
            Dictionary mapping tile ID -> list of AnimationSequence
        """
        animations = {}
        for tileset in json_data["tilesets"]:
            firstgid = tileset["firstgid"]
            for tile in tileset.get("tiles", []):
                if "animation" in tile:
                    tile_id = firstgid + tile["id"]
                    anim_frames = []
                    for frame in tile["animation"]:
                        frame_id = firstgid + frame["tileid"]
                        image_position = divmod(
                            frame_id - firstgid, sheet.sheet.get_size()[0] // tile_size
                        )
                        image_position = (
                            image_position[1] * tile_size,
                            image_position[0] * tile_size,
                        )
                        frame_image = sheet.image_at(
                            pygame.Rect(image_position, (tile_size, tile_size))
                        )
                        frame_image.set_colorkey((0, 0, 0))
                        anim_frames.append(frame_image)
                    if anim_frames:
                        animations[tile_id] = [
                            AnimationSequence(anim_frames, True, tile["animation"][0]["duration"])
                        ]
        return animations

    def _create_layer_sprites(
        self,
        layer: dict[str, Any],
        json_data: dict[str, Any],
        sheet: SpriteSheet,
        tile_size: int,
        layer_index: int,
        hitboxes: dict[int, HitBox],
        animations: dict[int, list[AnimationSequence]],
    ) -> list[BaseSprite]:
        """Creates sprites for a specific layer.

        Args:
            layer: Layer data
            json_data: JSON data of the map
            sheet: SpriteSheet of the tileset
            tile_size: Size of tiles
            layer_index: Layer index
            hitboxes: Dictionary of hitboxes
            animations: Dictionary of animations

        Returns:
            List of BaseSprite for the layer
        """
        sprites = []
        map_width = json_data["width"]

        for tile_index, tile_id in enumerate(layer["data"]):
            if tile_id != 0:  # 0 = empty tile
                tile_position = divmod(tile_index, map_width)
                tile_position = (
                    tile_position[1] * tile_size,
                    tile_position[0] * tile_size,
                )

                image = self._get_tile_image(tile_id, sheet, tile_size)

                sprite = BaseSprite(position=tile_position, layer=layer_index, image=image)

                if tile_id in hitboxes:
                    original_hitbox = hitboxes[tile_id]
                    # Create a new HitBox instance for each sprite
                    new_hitbox = HitBox(original_hitbox.rect.copy())
                    body_component = SolidBodyComponent(box1=new_hitbox)
                    sprite.add_component(body_component)

                if tile_id in animations:
                    anim_component = AnimationComponent(animation1=animations[tile_id][0])
                    sprite.add_component(anim_component)

                sprites.append(sprite)

        return sprites

    def _get_tile_image(self, tile_id: int, sheet: SpriteSheet, tile_size: int) -> pygame.Surface:
        """Loads the image of a specific tile from the tileset.

        Args:
            tile_id: Tile ID (1-based)
            sheet: SpriteSheet of the tileset
            tile_size: Size of tiles

        Returns:
            Pygame surface of the tile
        """
        firstgid = 1
        image_id = tile_id - firstgid

        image_position = divmod(image_id, sheet.sheet.get_size()[0] // tile_size)
        image_position = (
            image_position[1] * tile_size,
            image_position[0] * tile_size,
        )

        image = sheet.image_at(pygame.Rect(image_position, (tile_size, tile_size)))
        image.set_colorkey((0, 0, 0))
        return image
