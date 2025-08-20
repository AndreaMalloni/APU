from collections.abc import Generator
import io
import json
from unittest.mock import MagicMock
import xml.etree.ElementTree as ET

import pygame
import pytest

from apu.loading import JSONMapLoader, TiledMapLoader, TMXMapLoader
from apu.objects.components import AnimationComponent, SolidBodyComponent
from apu.objects.entities import BaseSprite


@pytest.fixture(autouse=True)
def pygame_init() -> Generator[None, None, None]:
    pygame.init()
    yield
    pygame.quit()


def test_supports_format_json_tmx() -> None:
    assert JSONMapLoader().supports_format("dummy.json")
    assert not JSONMapLoader().supports_format("dummy.tmx")
    assert TMXMapLoader().supports_format("dummy.tmx")
    assert not TMXMapLoader().supports_format("dummy.json")


def test_tiled_map_loader_selects_correct_loader(monkeypatch: pytest.MonkeyPatch) -> None:
    mock_loader = JSONMapLoader()
    called = {}

    def mock_supports(path: str) -> bool:
        return path.endswith(".json")

    def mock_load(path: str, assets: str) -> list[BaseSprite]:
        called["args"] = (path, assets)
        return [MagicMock(), MagicMock()]

    monkeypatch.setattr(mock_loader, "supports_format", mock_supports)
    monkeypatch.setattr(mock_loader, "load", mock_load)
    loader = TiledMapLoader()
    loader.loaders = [mock_loader]

    sprites = loader.load("map.json", "assets_path")
    assert len(sprites) == 2
    assert called["args"] == ("map.json", "assets_path")


def test_tiled_map_loader_no_loader_supports() -> None:
    loader = TiledMapLoader()
    loader.loaders = []
    with pytest.raises(ValueError, match=r"No loader supports the file format: map\.unsupported"):
        loader.load("map.unsupported", "assets")


def test_json_map_loader_load_basic(monkeypatch: pytest.MonkeyPatch) -> None:
    class DummySpriteSheet:
        def __init__(self, path: str):
            self.sheet = pygame.Surface((16, 16))

        def image_at(self, rect: pygame.Rect) -> pygame.Surface:
            return pygame.Surface((16, 16))

    import apu.loading as loading

    monkeypatch.setattr(loading, "SpriteSheet", DummySpriteSheet)

    fake_json = {
        "tileheight": 16,
        "width": 1,
        "layers": [{"type": "tilelayer", "data": [1]}],
        "tilesets": [{"image": "tiles.png", "firstgid": 1}],
    }
    monkeypatch.setattr("pathlib.Path.open", lambda *a, **k: io.StringIO(json.dumps(fake_json)))

    mock_sprite = MagicMock(spec=BaseSprite)
    monkeypatch.setattr(loading, "BaseSprite", MagicMock(return_value=mock_sprite))

    loader = loading.JSONMapLoader()
    sprites = loader.load("map.json", "assets/")
    assert len(sprites) == 1
    mock_sprite.add_component.assert_not_called()


def test_tmx_map_loader_load_basic(monkeypatch: pytest.MonkeyPatch) -> None:
    class DummySpriteSheet:
        def __init__(self, path: str):
            self.sheet = pygame.Surface((16, 16))

        def image_at(self, rect: pygame.Rect) -> pygame.Surface:
            return pygame.Surface((16, 16))

    import apu.loading as loading

    monkeypatch.setattr(loading, "SpriteSheet", DummySpriteSheet)

    # Fake TMX XML
    root = ET.Element("map", tilewidth="16", tileheight="16", width="1")
    tileset = ET.SubElement(root, "tileset", firstgid="1")
    ET.SubElement(tileset, "image", source="tiles.png")
    layer = ET.SubElement(root, "layer")
    data = ET.SubElement(layer, "data", encoding="csv")
    data.text = "1"
    tmx_str = ET.tostring(root, encoding="unicode")
    monkeypatch.setattr(ET, "parse", lambda _: ET.ElementTree(ET.fromstring(tmx_str)))

    mock_sprite = MagicMock(spec=BaseSprite)
    monkeypatch.setattr(loading, "BaseSprite", MagicMock(return_value=mock_sprite))

    loader = loading.TMXMapLoader()
    sprites = loader.load("map.tmx", "assets/")
    assert len(sprites) == 1
    mock_sprite.add_component.assert_not_called()


# Test per il caricamento di hitbox
def test_json_map_loader_load_with_hitbox(monkeypatch: pytest.MonkeyPatch) -> None:
    class DummySpriteSheet:
        def __init__(self, path: str):
            self.sheet = pygame.Surface((16, 16))

        def image_at(self, rect: pygame.Rect) -> pygame.Surface:
            return pygame.Surface((16, 16))

    import apu.loading as loading

    monkeypatch.setattr(loading, "SpriteSheet", DummySpriteSheet)

    fake_json = {
        "tileheight": 16,
        "width": 1,
        "layers": [{"type": "tilelayer", "data": [1]}],
        "tilesets": [
            {
                "image": "tiles.png",
                "firstgid": 1,
                "tiles": [
                    {
                        "id": 0,
                        "objectgroup": {"objects": [{"x": 0, "y": 0, "width": 16, "height": 16}]},
                    }
                ],
            }
        ],
    }
    monkeypatch.setattr("pathlib.Path.open", lambda *a, **k: io.StringIO(json.dumps(fake_json)))

    mock_sprite = MagicMock(spec=BaseSprite)
    monkeypatch.setattr(loading, "BaseSprite", MagicMock(return_value=mock_sprite))

    loader = loading.JSONMapLoader()
    sprites = loader.load("map.json", "assets/")
    assert len(sprites) == 1
    mock_sprite.add_component.assert_called_once()
    assert isinstance(mock_sprite.add_component.call_args[0][0], SolidBodyComponent)


def test_tmx_map_loader_load_with_hitbox(monkeypatch: pytest.MonkeyPatch) -> None:
    class DummySpriteSheet:
        def __init__(self, path: str):
            self.sheet = pygame.Surface((16, 16))

        def image_at(self, rect: pygame.Rect) -> pygame.Surface:
            return pygame.Surface((16, 16))

    import apu.loading as loading

    monkeypatch.setattr(loading, "SpriteSheet", DummySpriteSheet)

    root = ET.Element("map", tilewidth="16", tileheight="16", width="1")
    tileset = ET.SubElement(root, "tileset", firstgid="1")
    ET.SubElement(tileset, "image", source="tiles.png")
    tile_with_obj = ET.SubElement(tileset, "tile", id="0")
    obj_group = ET.SubElement(tile_with_obj, "objectgroup")
    ET.SubElement(obj_group, "object", x="0", y="0", width="16", height="16")
    layer = ET.SubElement(root, "layer")
    data = ET.SubElement(layer, "data", encoding="csv")
    data.text = "1"
    tmx_str = ET.tostring(root, encoding="unicode")
    monkeypatch.setattr(ET, "parse", lambda _: ET.ElementTree(ET.fromstring(tmx_str)))

    mock_sprite = MagicMock(spec=BaseSprite)
    monkeypatch.setattr(loading, "BaseSprite", MagicMock(return_value=mock_sprite))

    loader = loading.TMXMapLoader()
    sprites = loader.load("map.tmx", "assets/")
    assert len(sprites) == 1
    mock_sprite.add_component.assert_called_once()
    assert isinstance(mock_sprite.add_component.call_args[0][0], SolidBodyComponent)


def test_json_map_loader_load_with_animation(monkeypatch: pytest.MonkeyPatch) -> None:
    class DummySpriteSheet:
        def __init__(self, path: str):
            self.sheet = pygame.Surface((32, 16))  # Dimensioni per due tile

        def image_at(self, rect: pygame.Rect) -> pygame.Surface:
            return pygame.Surface((16, 16))

    import apu.loading as loading

    monkeypatch.setattr(loading, "SpriteSheet", DummySpriteSheet)

    fake_json = {
        "tileheight": 16,
        "width": 1,
        "layers": [{"type": "tilelayer", "data": [1]}],
        "tilesets": [
            {
                "image": "tiles.png",
                "firstgid": 1,
                "tilewidth": 16,
                "tiles": [
                    {
                        "id": 0,
                        "animation": [
                            {"duration": 100, "tileid": 0},
                            {"duration": 100, "tileid": 1},
                        ],
                    }
                ],
            }
        ],
    }
    monkeypatch.setattr("pathlib.Path.open", lambda *a, **k: io.StringIO(json.dumps(fake_json)))

    mock_sprite = MagicMock(spec=BaseSprite)
    monkeypatch.setattr(loading, "BaseSprite", MagicMock(return_value=mock_sprite))

    loader = loading.JSONMapLoader()
    sprites = loader.load("map.json", "assets/")
    assert len(sprites) == 1
    mock_sprite.add_component.assert_called_once()
    assert isinstance(mock_sprite.add_component.call_args[0][0], AnimationComponent)


def test_tmx_map_loader_load_with_animation(monkeypatch: pytest.MonkeyPatch) -> None:
    class DummySpriteSheet:
        def __init__(self, path: str):
            self.sheet = pygame.Surface((32, 16))  # Dimensioni per due tile

        def image_at(self, rect: pygame.Rect) -> pygame.Surface:
            return pygame.Surface((16, 16))

    import apu.loading as loading

    monkeypatch.setattr(loading, "SpriteSheet", DummySpriteSheet)

    root = ET.Element("map", tilewidth="16", tileheight="16", width="1")
    tileset = ET.SubElement(root, "tileset", firstgid="1")
    ET.SubElement(tileset, "image", source="tiles.png")
    tile_with_anim = ET.SubElement(tileset, "tile", id="0")
    animation = ET.SubElement(tile_with_anim, "animation")
    ET.SubElement(animation, "frame", tileid="0", duration="100")
    ET.SubElement(animation, "frame", tileid="1", duration="100")
    layer = ET.SubElement(root, "layer")
    data = ET.SubElement(layer, "data", encoding="csv")
    data.text = "1"
    tmx_str = ET.tostring(root, encoding="unicode")
    monkeypatch.setattr(ET, "parse", lambda _: ET.ElementTree(ET.fromstring(tmx_str)))

    mock_sprite = MagicMock(spec=BaseSprite)
    monkeypatch.setattr(loading, "BaseSprite", MagicMock(return_value=mock_sprite))

    loader = loading.TMXMapLoader()
    sprites = loader.load("map.tmx", "assets/")
    assert len(sprites) == 1
    mock_sprite.add_component.assert_called_once()
    assert isinstance(mock_sprite.add_component.call_args[0][0], AnimationComponent)
