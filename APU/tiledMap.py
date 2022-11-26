import pygame as pg
import pytmx as tmx
import os
from APU.core.baseSpriteObject import BaseSpriteObject
from APU.core.config import TILE_SIZE, DEFAULT_RESOLUTION

class TiledMap():
    def __init__(self, path) -> None:
        if not os.path.exists(path): 
            raise FileNotFoundError(f"Map file not found: {path}")

        self._tmxMapObject = tmx.load_pygame(path)

    @property
    def tmxMapObject(self) -> tmx.TiledMap:
        return self._tmxMapObject

    def toLayeredGroupLoose(self) -> pg.sprite.LayeredUpdates:
        layeredGroup = pg.sprite.LayeredUpdates()
        for layer in self.tmxMapObject.visible_layers:
            if isinstance(layer, tmx.TiledTileLayer):
                for tile in layer.tiles():
                    tileImage = tile[2]
                    tileX, tileY = tile[0] * TILE_SIZE, tile[1] * TILE_SIZE
                    if tileImage is not None: layeredGroup.add(BaseSpriteObject(tileX, tileY, layer.properties["level"], tileImage))
        return layeredGroup

    def toLayeredGroupCompact(self) -> pg.sprite.LayeredUpdates:

        def getTiles(layer):
            tiles = []
            for tile in layer.tiles():
                tileX, tileY = tile[0] * TILE_SIZE, tile[1] * TILE_SIZE
                if tileImage := tile[2]:
                    tiles.append((tileX, tileY, tileImage))
            return tiles
           
        layeredGroup = pg.sprite.LayeredUpdates()

        for layer in self.tmxMapObject.visible_layers:
            layerSurface = pg.Surface(DEFAULT_RESOLUTION)
            layerSurface.set_colorkey((0, 0, 0))
            if isinstance(layer, tmx.TiledTileLayer):
                tiles = getTiles(layer)
                if len(tiles) != 0:
                    for tile in tiles:
                        layerSurface.blit(tile[2].convert_alpha(), (tile[0], tile[1]))
                    layeredGroup.add(BaseSpriteObject(0, 0, layer.properties["level"], layerSurface))
        return layeredGroup

    def getObjectsByLayerName(self, layer:str):
        objects = []

        for objectLayer in self._tmxMapObject.objectgroups:
            if objectLayer.name == layer:
                objects.extend(iter(objectLayer))
        return objects

    def getObjectsByName(self, name):
        objects = []

        for objectLayer in self._tmxMapObject.objectgroups:
            objects.extend(gameObject for gameObject in objectLayer if gameObject.name == name)

        return objects

