from collections.abc import Callable, Iterator
from typing import Any, Generic, TypeVar

import pygame
from typing_extensions import override

from apu.camera import Camera
from apu.core.const import (
    NEIGHBOUR_MATRIX,
    SCENE_CUSTOM,
    SCENE_ENTER,
    SCENE_EXIT,
    SCENE_PAUSE,
    SCENE_RESUME,
)
from apu.core.enums import RenderLayer, SceneState
from apu.objects.components import MovementComponent
from apu.objects.entities import BaseSprite
from apu.scene.node import SceneNode

__all__ = ["Scene", "TiledScene"]

T = TypeVar("T")


class Scene(SceneNode, Generic[T]):
    """
    Base class for all scenes.
    Provides a flexible and generic architecture for managing game content.
    """

    def __init__(self, name: str, camera: Camera | None = None):
        super().__init__(name)
        self.camera = camera or Camera()
        self._items: dict[RenderLayer, list[T]] = {layer: [] for layer in RenderLayer}
        self._custom_layers: dict[str, list[T]] = {}
        self._update_handlers: list[Callable[[float], None]] = []
        self._render_handlers: list[Callable[[pygame.Surface, Camera], None]] = []
        self._transition_data: dict[str, Any] = {}

    def add_item(self, item: T, layer: RenderLayer | str = RenderLayer.ENTITIES) -> None:
        """Adds an item to the scene"""
        if isinstance(layer, RenderLayer):
            self._items[layer].append(item)
        else:
            if layer not in self._custom_layers:
                self._custom_layers[layer] = []
            self._custom_layers[layer].append(item)

    def remove_item(self, item: T) -> None:
        """Removes an item from the scene"""
        for layer_items in self._items.values():
            if item in layer_items:
                layer_items.remove(item)
                return
        for layer_items in self._custom_layers.values():
            if item in layer_items:
                layer_items.remove(item)
                return

    def get_items(self, layer: RenderLayer | str) -> list[T]:
        """Gets all items in a layer"""
        if isinstance(layer, RenderLayer):
            return self._items[layer].copy()
        return self._custom_layers.get(layer, []).copy()

    def find_items(self, predicate: Callable[[T], bool]) -> Iterator[T]:
        """Finds items that satisfy a predicate"""
        for layer_items in self._items.values():
            for item in layer_items:
                if predicate(item):
                    yield item
        for layer_items in self._custom_layers.values():
            for item in layer_items:
                if predicate(item):
                    yield item

    def add_update_handler(self, handler: Callable[[float], None]) -> None:
        """Adds an update handler"""
        self._update_handlers.append(handler)

    def add_render_handler(self, handler: Callable[[pygame.Surface, Camera], None]) -> None:
        """Adds a render handler"""
        self._render_handlers.append(handler)

    def on_enter(self, transition_data: dict[str, Any] | None = None) -> None:
        """Called when the scene becomes active"""
        self.state = SceneState.ACTIVE
        self._transition_data = transition_data or {}

        # Emit custom pygame event
        event = pygame.event.Event(
            SCENE_ENTER, {"scene_name": self.name, "data": self._transition_data}
        )
        pygame.event.post(event)

    def on_exit(self) -> None:
        """Called when the scene becomes inactive"""
        self.state = SceneState.INACTIVE

        # Emit custom pygame event
        event = pygame.event.Event(SCENE_EXIT, {"scene_name": self.name, "data": {}})
        pygame.event.post(event)

    def on_pause(self) -> None:
        """Called when the scene is paused"""
        self.state = SceneState.PAUSED

        # Emit custom pygame event
        event = pygame.event.Event(SCENE_PAUSE, {"scene_name": self.name, "data": {}})
        pygame.event.post(event)

    def on_resume(self) -> None:
        """Called when the scene resumes"""
        self.state = SceneState.ACTIVE

        # Emit custom pygame event
        event = pygame.event.Event(SCENE_RESUME, {"scene_name": self.name, "data": {}})
        pygame.event.post(event)

    def emit_scene_event(self, event_type: str, data: dict[str, Any] | None = None) -> None:
        """Emits a custom scene event as a pygame event"""
        event = pygame.event.Event(
            SCENE_CUSTOM, {"scene_name": self.name, "event_type": event_type, "data": data or {}}
        )
        pygame.event.post(event)

    @override
    def update(self, dt: float) -> None:
        """Updates the scene"""
        if self.state != SceneState.ACTIVE:
            return

        # Update the camera
        self.camera.update(dt) if hasattr(self.camera, "update") else None

        # Update all items
        for layer_items in self._items.values():
            for item in layer_items:
                if hasattr(item, "update"):
                    item.update()

        for layer_items in self._custom_layers.values():
            for item in layer_items:
                if hasattr(item, "update"):
                    item.update()

        # Execute update handlers
        for handler in self._update_handlers:
            try:
                handler(dt)
            except Exception as e:
                print(f"Error in update handler: {e}")

    @override
    def render(self, surface: pygame.Surface, camera: Camera | None = None) -> None:
        """Renders the scene"""
        if not self.visible:
            return

        render_camera = camera or self.camera

        # Execute pre-render handlers
        for handler in self._render_handlers:
            try:
                handler(surface, render_camera)
            except Exception as e:
                print(f"Error in render handler: {e}")

        # Render all layers in order
        for layer in RenderLayer:
            self._render_layer(surface, render_camera, self._items[layer])

        # Render custom layers
        for _layer_name, layer_items in sorted(self._custom_layers.items()):
            self._render_layer(surface, render_camera, layer_items)

    def _render_layer(self, surface: pygame.Surface, camera: Camera, items: list[T]) -> None:
        """Renders a specific layer"""
        for item in items:
            if hasattr(item, "draw"):
                item.draw(surface)
            elif hasattr(item, "render"):
                item.render(surface, camera)

    def __iter__(self) -> Iterator[T]:
        """Iterates over all items in the scene"""
        for layer_items in self._items.values():
            yield from layer_items
        for layer_items in self._custom_layers.values():
            yield from layer_items


class TiledScene(Scene[BaseSprite]):
    """
    Specialized scene for tile-based games.
    Maintains compatibility with the previous implementation.
    """

    def __init__(self, name: str, tile_size: int, camera: Camera | None = None):
        super().__init__(name, camera)
        self.tile_size = tile_size
        self._static_items: dict[int, dict[tuple[int, int], BaseSprite]] = {}
        self._dynamic_items: pygame.sprite.Group[BaseSprite] = pygame.sprite.Group()

    def insert(self, *items: BaseSprite) -> None:
        """Inserts sprites into the scene (compatibility)"""
        for item in items:
            if item.get_component(MovementComponent) is None:
                if item.layer not in self._static_items:
                    self._static_items[item.layer] = {}
                self._static_items[item.layer][item.position] = item
                self.add_item(item, RenderLayer.TERRAIN)
            else:
                self._dynamic_items.add(item)
                self.add_item(item, RenderLayer.ENTITIES)

    def remove(self, *items: BaseSprite) -> None:
        """Removes sprites from the scene (compatibility)"""
        for item in items:
            if item.get_component(MovementComponent) is None:
                if item.layer in self._static_items:
                    self._static_items[item.layer].pop(item.position, None)
            else:
                self._dynamic_items.remove(item)
            self.remove_item(item)

    def has(self, item: BaseSprite) -> bool:
        """Checks if an item is in the scene (compatibility)"""
        return (
            item.layer in self._static_items
            and item.position in self._static_items[item.layer]
            and self._static_items[item.layer][item.position] is item
        )

    def neighbours(self, item: BaseSprite) -> list[BaseSprite]:
        """Finds the neighbors of an item (compatibility)"""
        position = item.position
        layer = item.layer
        neighbour_tiles = []

        for offset in NEIGHBOUR_MATRIX:
            neighbour_position = (
                position[0] + offset[0] * self.tile_size,
                position[1] + offset[1] * self.tile_size,
            )
            if neighbour_position in self._static_items[layer]:
                neighbour_tiles.append(self._static_items[layer][neighbour_position])
        return neighbour_tiles

    @override
    def update(self, dt: float) -> None:
        """Updates the tile-based scene"""
        super().update(dt)

        # Update dynamic sprites
        self._dynamic_items.update()

        # Update static sprites
        for layer in self._static_items:
            for position in self._static_items[layer]:
                self._static_items[layer][position].update()
