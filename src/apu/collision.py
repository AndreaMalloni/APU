from __future__ import annotations

from typing import TYPE_CHECKING

import pygame
from typing_extensions import override

if TYPE_CHECKING:
    from apu.objects.components import SolidBodyComponent


class HitBox:
    def __init__(self, rect: pygame.rect.Rect, visible: bool = False) -> None:
        self._body: SolidBodyComponent | None = None
        self.rect = rect
        self.visible = visible
        self.border_width = 1
        self.border_color = (255, 0, 0)

    def absolute_rect(self, offset: tuple[int, int]) -> pygame.Rect:
        """Returns an offsetted rect object, based on the entity position."""
        return self.rect.move(offset)

    def draw(self, surface: pygame.surface.Surface) -> None:
        if self.visible and self._body is not None and self._body.entity is not None:
            pygame.draw.rect(
                surface,
                self.border_color,
                self.absolute_rect(self._body.entity.position),
                width=self.border_width,
            )

    @override
    def __str__(self) -> str:
        return f"""
        Rect: {self.rect} 
        Visible: {self.visible} 
        Border width: {self.border_width} 
        Border color: {self.border_color} 
        """
