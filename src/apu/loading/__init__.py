from typing_extensions import override

from apu.loading.json_loader import JSONMapLoader
from apu.loading.loader_base import MapLoader
from apu.loading.tmx_loader import TMXMapLoader
from apu.objects.entities import BaseSprite

__all__ = ["JSONMapLoader", "MapLoader", "TMXMapLoader", "TiledMapLoader"]


class TiledMapLoader(MapLoader):
    """Main loader for Tiled maps that delegates to specific loaders."""

    def __init__(self) -> None:
        self.loaders: list[MapLoader] = [
            JSONMapLoader(),
            TMXMapLoader(),
        ]

    def add_loader(self, loader: MapLoader) -> None:
        """Adds a new loader to the list of supported loaders.

        Args:
            loader: The loader to add
        """
        self.loaders.append(loader)

    @override
    def load(self, map_path: str, assets_path: str) -> list[BaseSprite]:
        """Loads a map using the appropriate loader.

        Args:
            map_path: Path to the map file
            assets_path: Path to the assets directory

        Returns:
            List of BaseSprite representing the map elements

        Raises:
            ValueError: If no loader supports the file format
        """
        for loader in self.loaders:
            if loader.supports_format(map_path):
                return loader.load(map_path, assets_path)

        raise ValueError(f"No loader supports the file format: {map_path}")

    @override
    def supports_format(self, file_path: str) -> bool:
        """Checks if there's a loader that supports the file format.

        Args:
            file_path: Path to the file to check

        Returns:
            True if there's a loader that supports the format, False otherwise
        """
        return any(loader.supports_format(file_path) for loader in self.loaders)
