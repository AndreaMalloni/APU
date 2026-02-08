import base64
import gzip
import struct
import xml.etree.ElementTree as ET
import zlib

import pygame
from typing_extensions import override

from apu.collision import HitBox
from apu.core.spritesheet import AnimationSequence, SpriteSheet
from apu.loading.loader_base import MapLoader
from apu.objects.components import AnimationComponent, SolidBodyComponent
from apu.objects.entities import BaseSprite

__all__ = ["TMXMapLoader"]


class TMXMapLoader(MapLoader):
    """Loader for Tiled maps in TMX (XML) format."""

    @override
    def supports_format(self, file_path: str) -> bool:
        return file_path.lower().endswith(".tmx")

    @override
    def load(self, map_path: str, assets_path: str) -> list[BaseSprite]:
        """Loads a Tiled map from TMX file.

        Args:
            map_path: Path to the TMX map file
            assets_path: Path to the assets directory

        Returns:
            List of BaseSprite representing the map elements
        """
        tree = ET.parse(map_path)
        root = tree.getroot()

        tile_width = int(root.get("tilewidth", 16) or 16)
        tile_height = int(root.get("tileheight", 16) or 16)
        map_width = int(root.get("width", 0) or 0)

        tileset = root.find("tileset")
        if tileset is None:
            raise ValueError("No tileset found in TMX file")

        tileset_path = self._get_tileset_path(tileset, assets_path)
        sheet = SpriteSheet(tileset_path)

        hitboxes = self._load_objects_from_tmx(root)

        animations = self._load_animations_from_tmx(root, sheet, tile_width, tile_height)

        sprites = []
        for layer_index, layer in enumerate(root.findall("layer")):
            layer_sprites = self._create_layer_sprites_from_tmx(
                layer, map_width, tile_width, tile_height, layer_index, sheet, hitboxes, animations
            )
            sprites.extend(layer_sprites)

        return sprites

    def _get_tileset_path(self, tileset: ET.Element, assets_path: str) -> str:
        """Extracts the tileset path from TMX.

        Args:
            tileset: Tileset element from TMX
            assets_path: Base path of assets

        Returns:
            Complete path to the tileset file
        """
        image = tileset.find("image")
        if image is not None:
            source = image.get("source")
            if source is not None:
                return str(assets_path + source)
        # Fallback for external tilesets
        return str(assets_path + "tileset.png")

    def _get_firstgid(self, root: ET.Element) -> int:
        """Helper to get the firstgid of the tileset from TMX.

        Args:
            root: Root element of TMX

        Returns:
            The firstgid of the tileset.
        """
        tileset = root.find("tileset")
        if tileset is None:
            raise ValueError("No tileset found in TMX file")
        return int(tileset.get("firstgid", 1) or 1)

    def _load_objects_from_tmx(self, root: ET.Element) -> dict[int, HitBox]:
        """Loads object information from TMX.

        Args:
            root: Root element of TMX

        Returns:
            Dictionary mapping tile ID -> HitBox for hitboxes
        """
        objects = {}
        firstgid = self._get_firstgid(root)

        for tileset in root.findall("tileset"):
            for tile in tileset.findall("tile"):
                tile_id = int(tile.get("id", 0) or 0)
                objectgroup = tile.find("objectgroup")

                if objectgroup is not None:
                    for obj in objectgroup.findall("object"):
                        x = float(obj.get("x", 0) or 0)
                        y = float(obj.get("y", 0) or 0)
                        width = float(obj.get("width", 0) or 0)
                        height = float(obj.get("height", 0) or 0)

                        objects[firstgid + tile_id] = HitBox(pygame.Rect(x, y, width, height))

        return objects

    def _load_animations_from_tmx(
        self, root: ET.Element, sheet: SpriteSheet, tile_width: int, tile_height: int
    ) -> dict[int, list[AnimationSequence]]:
        """Loads animation information from TMX.

        Args:
            root: Root element of TMX
            sheet: SpriteSheet of the tileset
            tile_width: Width of tiles
            tile_height: Height of tiles

        Returns:
            Dictionary mapping tile ID -> list of AnimationSequence
        """
        animations = {}
        firstgid = self._get_firstgid(root)

        for tileset in root.findall("tileset"):
            for tile in tileset.findall("tile"):
                tile_id = int(tile.get("id", 0) or 0)
                animation = tile.find("animation")

                if animation is not None:
                    anim_frames = []
                    duration = 0

                    for frame in animation.findall("frame"):
                        frame_id = int(frame.get("tileid", 0) or 0)
                        frame_duration = int(frame.get("duration", 100) or 100)
                        duration = frame_duration

                        image_position = divmod(frame_id, sheet.sheet.get_size()[0] // tile_width)
                        image_position = (
                            image_position[1] * tile_width,
                            image_position[0] * tile_height,
                        )

                        frame_image = sheet.image_at(
                            pygame.Rect(image_position, (tile_width, tile_height))
                        )
                        frame_image.set_colorkey((0, 0, 0))
                        anim_frames.append(frame_image)

                    if anim_frames:
                        # Use GID as key for consistency with layer data
                        animations[firstgid + tile_id] = [
                            AnimationSequence(anim_frames, True, duration)
                        ]

        return animations

    def _create_layer_sprites_from_tmx(
        self,
        layer: ET.Element,
        map_width: int,
        tile_width: int,
        tile_height: int,
        layer_index: int,
        sheet: SpriteSheet,
        hitboxes: dict[int, HitBox],
        animations: dict[int, list[AnimationSequence]],
    ) -> list[BaseSprite]:
        """Creates sprites for a specific layer from TMX.

        Args:
            layer: Layer element from TMX
            map_width: Width of the map
            tile_width: Width of tiles
            tile_height: Height of tiles
            layer_index: Layer index
            sheet: SpriteSheet of the tileset
            hitboxes: Dictionary of hitboxes
            animations: Dictionary of animations

        Returns:
            List of BaseSprite for the layer
        """
        sprites: list[BaseSprite] = []

        data = layer.find("data")
        if data is None:
            return sprites

        encoding = data.get("encoding") or ""
        compression = data.get("compression") or ""

        if encoding == "csv":
            if data.text is None:
                return sprites
            tile_data = [int(x) for x in data.text.strip().split(",")]
        elif encoding == "base64":
            if data.text is None:
                return sprites
            decoded_data = base64.b64decode(data.text.strip())
            if compression == "gzip":
                decoded_data = gzip.decompress(decoded_data)
            elif compression == "zlib":
                decoded_data = zlib.decompress(decoded_data)

            # Decode data as 32-bit integer array
            tile_data = []
            for i in range(0, len(decoded_data), 4):
                tile_id = struct.unpack("<I", decoded_data[i : i + 4])[0]
                tile_data.append(tile_id)
        else:
            # Unsupported format
            return sprites

        # Create sprites
        for tile_index, tile_id in enumerate(tile_data):
            if tile_id != 0:  # 0 = empty tile
                tile_position = divmod(tile_index, map_width)
                tile_position = (
                    tile_position[1] * tile_width,
                    tile_position[0] * tile_height,
                )

                image = self._get_tile_image_from_tmx(tile_id, sheet, tile_width, tile_height)

                sprite = BaseSprite(position=tile_position, layer=layer_index, image=image)

                if tile_id in hitboxes:
                    original_hitbox = hitboxes[tile_id]
                    new_hitbox = HitBox(original_hitbox.rect.copy())
                    body_component = SolidBodyComponent(box1=new_hitbox)
                    sprite.add_component(body_component)

                if tile_id in animations:
                    anim_component = AnimationComponent(animation1=animations[tile_id][0])
                    sprite.add_component(anim_component)

                sprites.append(sprite)

        return sprites

    def _get_tile_image_from_tmx(
        self, tile_id: int, sheet: SpriteSheet, tile_width: int, tile_height: int
    ) -> pygame.Surface:
        """Loads the image of a specific tile from the tileset for TMX.

        Args:
            tile_id: Tile ID (1-based)
            sheet: SpriteSheet of the tileset
            tile_width: Width of tiles
            tile_height: Height of tiles

        Returns:
            Pygame surface of the tile
        """
        firstgid = 1
        image_id = tile_id - firstgid

        image_position = divmod(image_id, sheet.sheet.get_size()[0] // tile_width)
        image_position = (
            image_position[1] * tile_width,
            image_position[0] * tile_height,
        )

        image = sheet.image_at(pygame.Rect(image_position, (tile_width, tile_height)))
        image.set_colorkey((0, 0, 0))
        return image
