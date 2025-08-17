from typing import Any, Optional

import pygame

from apu.objects.components import BaseComponent


class BaseSprite(pygame.sprite.Sprite):
    """
    Represents a generic static sprite and provides methods
    to draw itself on the (pygame) display and get the current position/size.
    """

    def __init__(
        self, position: tuple[int, int], layer: int = 0, image: Optional[pygame.Surface] = None
    ) -> None:
        """Constructs a sprite object with basic functionality.

        Args:
            position (tuple): x and y coordinates of the sprite.
            layer (int, optional): the layer to draw the image to. Defaults to 0.
            image (pygame.Surface, optional): default image to draw. Defaults to empty surface.
        """
        self._layer = layer
        super().__init__()
        self.image = image if image is not None else pygame.Surface((0, 0))
        self.x: int = position[0]
        self.y: int = position[1]

        self.components: dict[str, BaseComponent] = {}

    def add_component(self, component: BaseComponent) -> None:
        name = type(component).__name__
        self.components[name] = component
        component.entity = self
        component.on_added()

    def remove_component(self, component_type: type[BaseComponent]) -> None:
        comp = self.components.pop(component_type.__name__, None)
        if comp:
            comp.on_removed()

    def get_component(self, component_type: type[BaseComponent]) -> BaseComponent | None:
        return self.components.get(component_type.__name__)

    def __getattr__(self, name: str) -> Any:
        # Delegazione: se l'attributo non esiste nell'entità, cerca nei componenti
        for component in self.components.values():
            if hasattr(component, name):
                return getattr(component, name)
        raise AttributeError(f"{self.__class__.__name__} has no attribute {name}")

    @property
    def position(self) -> tuple[int, int]:
        """Returns a vector of int values (x position, y position)."""
        return self.x, self.y

    @property
    def size(self) -> tuple[int, int]:
        """Returns a tuple of int values (width, height)."""
        if self.image is not None:
            size: tuple[int, int] = self.image.get_size()
            return (size[0], size[1])
        return (0, 0)

    @property
    def computed_rect(self) -> pygame.rect.Rect:
        if self.image is not None:
            return self.image.get_rect(topleft=self.position)
        return pygame.Rect(self.position, (0, 0))

    def draw(self, window: pygame.Surface, flags: int = 0) -> None:
        """
        Draws the sprite image on the given (pygame) display in the current (x, y) position.

        Args:
            :param window: display to draw the image to.
            :param flags: pygame special_flags
        """
        if self.image is not None:
            window.blit(self.image, self.position, special_flags=flags)

        for component in self.components.values():
            component.draw(window)

    def update(self) -> None:
        for component in self.components.values():
            component.update()

    def __str__(self) -> str:
        result = [
            f"BaseSprite(position={self.position}, layer={self._layer}, size={self.size})",
            "Components:"
        ]
        if self.components:
            for name, component in self.components.items():
                result.append(f"  {name}: {component}")
        else:
            result.append("  None")
        return "\n".join(result)


if __name__ == "__main__":
    print("All imports working!")
