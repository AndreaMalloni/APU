from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from typing import Any, Optional

import pygame

from apu.camera import Camera
from apu.core.enums import SceneState

__all__ = ["SceneNode", "SceneTransition"]


@dataclass
class SceneTransition:
    """Represents a transition between scenes"""

    from_scene: str
    to_scene: str
    transition_type: str = "fade"
    duration: float = 1.0
    data: dict[str, Any] = field(default_factory=dict)


class SceneNode(ABC):
    """Base node for the scene hierarchy"""

    def __init__(self, name: str):
        self.name = name
        self.parent: SceneNode | None = None
        self.children: list[SceneNode] = []
        self.state: SceneState = SceneState.INACTIVE
        self.visible = True
        self.enabled = True

    def add_child(self, child: "SceneNode") -> None:
        """Adds a child to the hierarchy"""
        if child.parent:
            child.parent.remove_child(child)
        child.parent = self
        self.children.append(child)

    def remove_child(self, child: "SceneNode") -> None:
        """Removes a child from the hierarchy"""
        if child in self.children:
            self.children.remove(child)
            child.parent = None

    def find_child(self, name: str) -> Optional["SceneNode"]:
        """Finds a child by name"""
        for child in self.children:
            if child.name == name:
                return child
            result = child.find_child(name)
            if result:
                return result
        return None

    def get_root(self) -> "SceneNode":
        """Gets the root node of the hierarchy"""
        if self.parent:
            return self.parent.get_root()
        return self

    def update_hierarchy(self, dt: float) -> None:
        """Updates the complete hierarchy"""
        if not self.enabled:
            return

        self.update(dt)
        for child in self.children:
            child.update_hierarchy(dt)

    def render_hierarchy(self, surface: pygame.Surface, camera: Camera | None = None) -> None:
        """Renders the complete hierarchy"""
        if not self.visible:
            return

        self.render(surface, camera)
        for child in self.children:
            child.render_hierarchy(surface, camera)

    @abstractmethod
    def update(self, dt: float) -> None:
        """Updates the node"""

    @abstractmethod
    def render(self, surface: pygame.Surface, camera: Camera | None = None) -> None:
        """Renders the node"""

