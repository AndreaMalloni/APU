from abc import ABC, abstractmethod

from apu.objects.entities import BaseSprite

__all__ = ["MapLoader"]


class MapLoader(ABC):
    """Abstract base class for all map loaders.

    This class defines the common interface for all map loaders,
    allowing easy extension of support for new formats.
    """

    @abstractmethod
    def load(self, map_path: str, assets_path: str) -> list[BaseSprite]:
        """Loads a map and returns a list of sprites.

        Args:
            map_path: Path to the map file
            assets_path: Path to the assets directory

        Returns:
            List of BaseSprite representing the map elements
        """

    @abstractmethod
    def supports_format(self, file_path: str) -> bool:
        """Checks if this loader supports the specified file format.

        Args:
            file_path: Path to the file to check

        Returns:
            True if the format is supported, False otherwise
        """

