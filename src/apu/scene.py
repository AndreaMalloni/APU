from abc import ABC, abstractmethod
from collections.abc import Callable, Iterator
from dataclasses import dataclass, field
from enum import Enum, auto
from typing import Any, Generic, Optional, TypeVar

import pygame
from typing_extensions import override

from apu.core.enums import NEIGHBOUR_MATRIX
from apu.objects.components import MovementComponent
from apu.objects.entities import BaseSprite

__all__ = [
    "SCENE_EVENT_TYPES",
    "RenderLayer",
    "Scene",
    "SceneManager",
    "SceneNode",
    "SceneState",
    "SceneTransition",
    "TiledScene",
]


# Eventi pygame personalizzati per le scene
SCENE_ENTER = pygame.USEREVENT + 1
SCENE_EXIT = pygame.USEREVENT + 2
SCENE_PAUSE = pygame.USEREVENT + 3
SCENE_RESUME = pygame.USEREVENT + 4
SCENE_CUSTOM = pygame.USEREVENT + 5

SCENE_EVENT_TYPES = {
    "scene_enter": SCENE_ENTER,
    "scene_exit": SCENE_EXIT,
    "scene_pause": SCENE_PAUSE,
    "scene_resume": SCENE_RESUME,
    "scene_custom": SCENE_CUSTOM,
}


class SceneState(Enum):
    """Stati possibili di una scena"""

    INACTIVE = auto()
    LOADING = auto()
    ACTIVE = auto()
    PAUSED = auto()
    TRANSITIONING = auto()
    UNLOADING = auto()


class RenderLayer(Enum):
    """Livelli di rendering predefiniti"""

    BACKGROUND = auto()
    TERRAIN = auto()
    DECORATIONS = auto()
    ENTITIES = auto()
    UI = auto()
    OVERLAY = auto()


@dataclass
class SceneTransition:
    """Rappresenta una transizione tra scene"""

    from_scene: str
    to_scene: str
    transition_type: str = "fade"
    duration: float = 1.0
    data: dict[str, Any] = field(default_factory=dict)


T = TypeVar("T")
SceneT = TypeVar("SceneT", bound="Scene")


class SceneNode(ABC):
    """Nodo base per la gerarchia delle scene"""

    def __init__(self, name: str):
        self.name = name
        self.parent: SceneNode | None = None
        self.children: list[SceneNode] = []
        self.state = SceneState.INACTIVE
        self.visible = True
        self.enabled = True

    def add_child(self, child: "SceneNode") -> None:
        """Aggiunge un figlio alla gerarchia"""
        if child.parent:
            child.parent.remove_child(child)
        child.parent = self
        self.children.append(child)

    def remove_child(self, child: "SceneNode") -> None:
        """Rimuove un figlio dalla gerarchia"""
        if child in self.children:
            self.children.remove(child)
            child.parent = None

    def find_child(self, name: str) -> Optional["SceneNode"]:
        """Trova un figlio per nome"""
        for child in self.children:
            if child.name == name:
                return child
            result = child.find_child(name)
            if result:
                return result
        return None

    def get_root(self) -> "SceneNode":
        """Ottiene il nodo radice della gerarchia"""
        if self.parent:
            return self.parent.get_root()
        return self

    def update_hierarchy(self, dt: float) -> None:
        """Aggiorna la gerarchia completa"""
        if not self.enabled:
            return

        self.update(dt)
        for child in self.children:
            child.update_hierarchy(dt)

    def render_hierarchy(self, surface: pygame.Surface, camera: Optional["Camera"] = None) -> None:
        """Rende la gerarchia completa"""
        if not self.visible:
            return

        self.render(surface, camera)
        for child in self.children:
            child.render_hierarchy(surface, camera)

    @abstractmethod
    def update(self, dt: float) -> None:
        """Aggiorna il nodo"""
        pass

    @abstractmethod
    def render(self, surface: pygame.Surface, camera: Optional["Camera"] = None) -> None:
        """Rende il nodo"""
        pass


class Camera:
    """Camera per il rendering delle scene"""

    def __init__(self, position: tuple[float, float] = (0, 0), zoom: float = 1.0):
        self.position = list(position)
        self.zoom = zoom
        self.target_position = list(position)
        self.target_zoom = zoom
        self.smooth_factor = 0.1

    def follow(self, target: tuple[float, float], dt: float) -> None:
        """Segue un target con movimento fluido"""
        self.target_position = list(target)
        self.position[0] += (self.target_position[0] - self.position[0]) * self.smooth_factor * dt
        self.position[1] += (self.target_position[1] - self.position[1]) * self.smooth_factor * dt

    def world_to_screen(self, world_pos: tuple[float, float]) -> tuple[float, float]:
        """Converte coordinate mondo in coordinate schermo"""
        return (
            (world_pos[0] - self.position[0]) * self.zoom,
            (world_pos[1] - self.position[1]) * self.zoom,
        )

    def screen_to_world(self, screen_pos: tuple[float, float]) -> tuple[float, float]:
        """Converte coordinate schermo in coordinate mondo"""
        return (
            screen_pos[0] / self.zoom + self.position[0],
            screen_pos[1] / self.zoom + self.position[1],
        )


class Scene(SceneNode, Generic[T]):
    """
    Classe base per tutte le scene.
    Fornisce un'architettura flessibile e generica per gestire contenuti di gioco.
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
        """Aggiunge un elemento alla scena"""
        if isinstance(layer, RenderLayer):
            self._items[layer].append(item)
        else:
            if layer not in self._custom_layers:
                self._custom_layers[layer] = []
            self._custom_layers[layer].append(item)

    def remove_item(self, item: T) -> None:
        """Rimuove un elemento dalla scena"""
        for layer_items in self._items.values():
            if item in layer_items:
                layer_items.remove(item)
                return
        for layer_items in self._custom_layers.values():
            if item in layer_items:
                layer_items.remove(item)
                return

    def get_items(self, layer: RenderLayer | str) -> list[T]:
        """Ottiene tutti gli elementi di un layer"""
        if isinstance(layer, RenderLayer):
            return self._items[layer].copy()
        return self._custom_layers.get(layer, []).copy()

    def find_items(self, predicate: Callable[[T], bool]) -> Iterator[T]:
        """Trova elementi che soddisfano un predicato"""
        for layer_items in self._items.values():
            for item in layer_items:
                if predicate(item):
                    yield item
        for layer_items in self._custom_layers.values():
            for item in layer_items:
                if predicate(item):
                    yield item

    def add_update_handler(self, handler: Callable[[float], None]) -> None:
        """Aggiunge un handler per l'aggiornamento"""
        self._update_handlers.append(handler)

    def add_render_handler(self, handler: Callable[[pygame.Surface, Camera], None]) -> None:
        """Aggiunge un handler per il rendering"""
        self._render_handlers.append(handler)

    def on_enter(self, transition_data: dict[str, Any] | None = None) -> None:
        """Chiamato quando la scena diventa attiva"""
        self.state = SceneState.ACTIVE
        self._transition_data = transition_data or {}

        # Emette evento pygame personalizzato
        event = pygame.event.Event(
            SCENE_ENTER, {"scene_name": self.name, "data": self._transition_data}
        )
        pygame.event.post(event)

    def on_exit(self) -> None:
        """Chiamato quando la scena diventa inattiva"""
        self.state = SceneState.INACTIVE

        # Emette evento pygame personalizzato
        event = pygame.event.Event(SCENE_EXIT, {"scene_name": self.name, "data": {}})
        pygame.event.post(event)

    def on_pause(self) -> None:
        """Chiamato quando la scena viene messa in pausa"""
        self.state = SceneState.PAUSED

        # Emette evento pygame personalizzato
        event = pygame.event.Event(SCENE_PAUSE, {"scene_name": self.name, "data": {}})
        pygame.event.post(event)

    def on_resume(self) -> None:
        """Chiamato quando la scena riprende"""
        self.state = SceneState.ACTIVE

        # Emette evento pygame personalizzato
        event = pygame.event.Event(SCENE_RESUME, {"scene_name": self.name, "data": {}})
        pygame.event.post(event)

    def emit_scene_event(self, event_type: str, data: dict[str, Any] | None = None) -> None:
        """Emette un evento di scena personalizzato come evento pygame"""
        event = pygame.event.Event(
            SCENE_CUSTOM, {"scene_name": self.name, "event_type": event_type, "data": data or {}}
        )
        pygame.event.post(event)

    @override
    def update(self, dt: float) -> None:
        """Aggiorna la scena"""
        if self.state != SceneState.ACTIVE:
            return

        # Aggiorna la camera
        self.camera.update(dt) if hasattr(self.camera, "update") else None

        # Aggiorna tutti gli elementi
        for layer_items in self._items.values():
            for item in layer_items:
                if hasattr(item, "update"):
                    item.update()

        for layer_items in self._custom_layers.values():
            for item in layer_items:
                if hasattr(item, "update"):
                    item.update()

        # Esegui gli handler di aggiornamento
        for handler in self._update_handlers:
            try:
                handler(dt)
            except Exception as e:
                print(f"Errore nell'update handler: {e}")

    @override
    def render(self, surface: pygame.Surface, camera: Camera | None = None) -> None:
        """Rende la scena"""
        if not self.visible:
            return

        render_camera = camera or self.camera

        # Esegui gli handler di rendering pre-render
        for handler in self._render_handlers:
            try:
                handler(surface, render_camera)
            except Exception as e:
                print(f"Errore nel render handler: {e}")

        # Rendi tutti i layer in ordine
        for layer in RenderLayer:
            self._render_layer(surface, render_camera, self._items[layer])

        # Rendi i layer custom
        for _layer_name, layer_items in sorted(self._custom_layers.items()):
            self._render_layer(surface, render_camera, layer_items)

    def _render_layer(self, surface: pygame.Surface, camera: Camera, items: list[T]) -> None:
        """Rende un layer specifico"""
        for item in items:
            if hasattr(item, "draw"):
                item.draw(surface)
            elif hasattr(item, "render"):
                item.render(surface, camera)

    def __iter__(self) -> Iterator[T]:
        """Itera su tutti gli elementi della scena"""
        for layer_items in self._items.values():
            yield from layer_items
        for layer_items in self._custom_layers.values():
            yield from layer_items


class TiledScene(Scene[BaseSprite]):
    """
    Scena specializzata per giochi tile-based.
    Mantiene la compatibilità con l'implementazione precedente.
    """

    def __init__(self, name: str, tile_size: int, camera: Camera | None = None):
        super().__init__(name, camera)
        self.tile_size = tile_size
        self._static_items: dict[int, dict[tuple[int, int], BaseSprite]] = {}
        self._dynamic_items: pygame.sprite.Group[BaseSprite] = pygame.sprite.Group()

    def insert(self, *items: BaseSprite) -> None:
        """Inserisce sprite nella scena (compatibilità)"""
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
        """Rimuove sprite dalla scena (compatibilità)"""
        for item in items:
            if item.get_component(MovementComponent) is None:
                if item.layer in self._static_items:
                    self._static_items[item.layer].pop(item.position, None)
            else:
                self._dynamic_items.remove(item)
            self.remove_item(item)

    def has(self, item: BaseSprite) -> bool:
        """Verifica se un item è nella scena (compatibilità)"""
        return (
            item.layer in self._static_items
            and item.position in self._static_items[item.layer]
            and self._static_items[item.layer][item.position] is item
        )

    def neighbours(self, item: BaseSprite) -> list[BaseSprite]:
        """Trova i vicini di un item (compatibilità)"""
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
        """Aggiorna la scena tile-based"""
        super().update(dt)

        # Aggiorna gli sprite dinamici
        self._dynamic_items.update()

        # Aggiorna gli sprite statici
        for layer in self._static_items:
            for position in self._static_items[layer]:
                self._static_items[layer][position].update()


class SceneManager:
    """
    Gestore globale delle scene.
    Fornisce un sistema di gestione scene con transizioni e stack.
    """

    def __init__(self) -> None:
        self._scenes: dict[str, Scene] = {}
        self._active_scene: Scene | None = None
        self._scene_stack: list[Scene] = []
        self._transitions: list[SceneTransition] = []
        self._transition_time = 0.0
        self._current_transition: SceneTransition | None = None

    def register_scene(self, scene: Scene) -> None:
        """Registra una scena nel manager"""
        self._scenes[scene.name] = scene

    def unregister_scene(self, scene_name: str) -> None:
        """Rimuove una scena dal manager"""
        if scene_name in self._scenes:
            scene = self._scenes[scene_name]
            if scene == self._active_scene:
                self.pop_scene()
            del self._scenes[scene_name]

    def push_scene(self, scene_name: str, transition_data: dict[str, Any] | None = None) -> None:
        """Aggiunge una scena in cima allo stack"""
        if scene_name not in self._scenes:
            raise ValueError(f"Scena '{scene_name}' non registrata")

        scene = self._scenes[scene_name]

        # Metti in pausa la scena attuale
        if self._active_scene:
            self._active_scene.on_pause()
            self._scene_stack.append(self._active_scene)

        # Attiva la nuova scena
        self._active_scene = scene
        scene.on_enter(transition_data)

    def pop_scene(self) -> Scene | None:
        """Rimuove la scena in cima allo stack"""
        if not self._scene_stack:
            return None

        # Disattiva la scena attuale
        if self._active_scene:
            self._active_scene.on_exit()

        # Ripristina la scena precedente
        self._active_scene = self._scene_stack.pop()
        self._active_scene.on_resume()

        return self._active_scene

    def switch_scene(self, scene_name: str, transition_data: dict[str, Any] | None = None) -> None:
        """Cambia direttamente a una scena"""
        if scene_name not in self._scenes:
            raise ValueError(f"Scena '{scene_name}' non registrata")

        # Disattiva la scena attuale
        if self._active_scene:
            self._active_scene.on_exit()

        # Attiva la nuova scena
        self._active_scene = self._scenes[scene_name]
        self._active_scene.on_enter(transition_data)

        # Pulisci lo stack
        self._scene_stack.clear()

    def get_active_scene(self) -> Scene | None:
        """Ottiene la scena attualmente attiva"""
        return self._active_scene

    def update(self, dt: float) -> None:
        """Aggiorna il manager delle scene"""
        if self._active_scene:
            self._active_scene.update_hierarchy(dt)

    def render(self, surface: pygame.Surface) -> None:
        """Rende la scena attiva"""
        if self._active_scene:
            self._active_scene.render_hierarchy(surface)


# Istanza globale del SceneManager
_scene_manager: SceneManager | None = None


def get_scene_manager() -> SceneManager:
    """Ottiene l'istanza globale del SceneManager"""
    global _scene_manager
    if _scene_manager is None:
        _scene_manager = SceneManager()
    return _scene_manager


# Alias per comodità
scene_manager = get_scene_manager
