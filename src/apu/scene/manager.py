from typing import Any

import pygame

from apu.scene.node import SceneTransition
from apu.scene.scene import Scene

__all__ = ["SceneManager", "get_scene_manager", "scene_manager"]


class SceneManager:
    """
    Global scene manager.
    Provides a scene management system with transitions and stack.
    """

    def __init__(self) -> None:
        self._scenes: dict[str, Scene] = {}
        self._active_scene: Scene | None = None
        self._scene_stack: list[Scene] = []
        self._transitions: list[SceneTransition] = []
        self._transition_time = 0.0
        self._current_transition: SceneTransition | None = None

    def register_scene(self, scene: Scene) -> None:
        """Registers a scene in the manager"""
        self._scenes[scene.name] = scene

    def unregister_scene(self, scene_name: str) -> None:
        """Removes a scene from the manager"""
        if scene_name in self._scenes:
            scene = self._scenes[scene_name]
            if scene == self._active_scene:
                self.pop_scene()
            del self._scenes[scene_name]

    def push_scene(self, scene_name: str, transition_data: dict[str, Any] | None = None) -> None:
        """Pushes a scene on top of the stack"""
        if scene_name not in self._scenes:
            raise ValueError(f"Scene '{scene_name}' not registered")

        scene = self._scenes[scene_name]

        # Pause the current scene
        if self._active_scene:
            self._active_scene.on_pause()
            self._scene_stack.append(self._active_scene)

        # Activate the new scene
        self._active_scene = scene
        scene.on_enter(transition_data)

    def pop_scene(self) -> Scene | None:
        """Pops the scene from the top of the stack"""
        if not self._scene_stack:
            return None

        # Deactivate the current scene
        if self._active_scene:
            self._active_scene.on_exit()

        # Restore the previous scene
        self._active_scene = self._scene_stack.pop()
        self._active_scene.on_resume()

        return self._active_scene

    def switch_scene(self, scene_name: str, transition_data: dict[str, Any] | None = None) -> None:
        """Switches directly to a scene"""
        if scene_name not in self._scenes:
            raise ValueError(f"Scene '{scene_name}' not registered")

        # Deactivate the current scene
        if self._active_scene:
            self._active_scene.on_exit()

        # Activate the new scene
        self._active_scene = self._scenes[scene_name]
        self._active_scene.on_enter(transition_data)

        # Clear the stack
        self._scene_stack.clear()

    def get_active_scene(self) -> Scene | None:
        """Gets the currently active scene"""
        return self._active_scene

    def update(self, dt: float) -> None:
        """Updates the scene manager"""
        if self._active_scene:
            self._active_scene.update_hierarchy(dt)

    def render(self, surface: pygame.Surface) -> None:
        """Renders the active scene"""
        if self._active_scene:
            self._active_scene.render_hierarchy(surface)


# Global SceneManager instance
_scene_manager: SceneManager | None = None


def get_scene_manager() -> SceneManager:
    """Gets the global SceneManager instance"""
    global _scene_manager
    if _scene_manager is None:
        _scene_manager = SceneManager()
    return _scene_manager


# Alias for convenience
scene_manager = get_scene_manager

