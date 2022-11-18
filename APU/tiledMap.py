import pygame as pg
import pytmx as tmx
import os
from APU.core.baseSpriteObject import BaseSpriteObject
from APU.core.config import TILE_SIZE

class TiledMap():
    def __init__(self, path) -> None:
        if not os.path.exists(path): 
            raise FileNotFoundError(f"Map file not found: {path}")

        self._tmxMapObject = tmx.load_pygame(path)

    @property
    def tmxMapObject(self) -> tmx.TiledMap:
        return self._tmxMapObject

    def toLayeredGroup(self) -> pg.sprite.LayeredUpdates:
        layeredGroup = pg.sprite.LayeredUpdates()
        for layer in self.tmxMapObject.visible_layers:
            if isinstance(layer, tmx.TiledTileLayer):
                for tile in layer.tiles():
                    tileImage = tile[2]
                    tileX, tileY = tile[0] * TILE_SIZE, tile[1] * TILE_SIZE
                    if tileImage is not None: layeredGroup.add(BaseSpriteObject(tileX, tileY, layer.properties["level"], tileImage))
        return layeredGroup


