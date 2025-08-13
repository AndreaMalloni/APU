from collections.abc import Generator
import io
import json
import xml.etree.ElementTree as ET

import pygame
import pytest

from apu.loading import JSONMapLoader, TiledMapLoader, TMXMapLoader


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

    def mock_load(path: str, assets: str) -> list[str]:
        called["args"] = (path, assets)
        return ["sprite1", "sprite2"]

    monkeypatch.setattr(mock_loader, "supports_format", mock_supports)
    monkeypatch.setattr(mock_loader, "load", mock_load)
    loader = TiledMapLoader()
    loader.loaders = [mock_loader]

    sprites = loader.load("map.json", "assets_path")
    assert sprites == ["sprite1", "sprite2"]  # type: ignore[comparison-overlap]
    assert called["args"] == ("map.json", "assets_path")


def test_tiled_map_loader_no_loader_supports() -> None:
    loader = TiledMapLoader()
    loader.loaders = []
    with pytest.raises(ValueError, match=r"No loader supports the file format: map\.unsupported"):
        loader.load("map.unsupported", "assets")


def test_json_map_loader_load_basic(monkeypatch: pytest.MonkeyPatch) -> None:
    # Patch direttamente SpriteSheet usato nel loader
    class DummySpriteSheet:
        def __init__(self, path: str):
            self.sheet = pygame.Surface((16, 16))

        def image_at(self, rect: pygame.Rect) -> pygame.Surface:
            return pygame.Surface((16, 16))

    import apu.loading as loading

    monkeypatch.setattr(loading, "SpriteSheet", DummySpriteSheet)

    # Fake JSON
    fake_json = {
        "tileheight": 16,
        "width": 1,
        "layers": [{"type": "tilelayer", "data": [1]}],
        "tilesets": [{"image": "tiles.png"}],
    }
    monkeypatch.setattr("pathlib.Path.open", lambda *a, **k: io.StringIO(json.dumps(fake_json)))

    # Patch BaseSprite
    monkeypatch.setattr(
        loading,
        "BaseSprite",
        lambda position, layer, image: type(
            "B",
            (),
            {"add_hitbox": lambda self, **kw: None, "add_animation": lambda self, **kw: None},
        )(),
    )

    loader = loading.JSONMapLoader()
    sprites = loader.load("map.json", "assets/")
    assert len(sprites) == 1


def test_tmx_map_loader_load_basic(monkeypatch: pytest.MonkeyPatch) -> None:
    # Patch direttamente SpriteSheet usato nel loader
    class DummySpriteSheet:
        def __init__(self, path: str):
            self.sheet = pygame.Surface((16, 16))

        def image_at(self, rect: pygame.Rect) -> pygame.Surface:
            return pygame.Surface((16, 16))

    import apu.loading as loading

    monkeypatch.setattr(loading, "SpriteSheet", DummySpriteSheet)

    # Fake TMX XML
    root = ET.Element("map", tilewidth="16", tileheight="16", width="1")
    tileset = ET.SubElement(root, "tileset")
    ET.SubElement(tileset, "image", source="tiles.png")
    layer = ET.SubElement(root, "layer")
    data = ET.SubElement(layer, "data", encoding="csv")
    data.text = "1"
    tmx_str = ET.tostring(root, encoding="unicode")
    monkeypatch.setattr(ET, "parse", lambda _: ET.ElementTree(ET.fromstring(tmx_str)))

    # Patch BaseSprite
    monkeypatch.setattr(
        loading,
        "BaseSprite",
        lambda position, layer, image: type(
            "B",
            (),
            {"add_hitbox": lambda self, **kw: None, "add_animation": lambda self, **kw: None},
        )(),
    )

    loader = loading.TMXMapLoader()
    sprites = loader.load("map.tmx", "assets/")
    assert len(sprites) == 1
