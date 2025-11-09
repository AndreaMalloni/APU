def main() -> None:
    print("Hello from apu!")


# Esportazioni per il sistema di event dispatcher
from .events import (
    event_dispatcher,
    get_event_dispatcher,
    EventDispatcher,
    EventCondition,
    EventHandler,
)

# Esportazioni per il sistema di scene
from .scene import (
    Scene,
    TiledScene,
    SceneManager,
    scene_manager,
    SceneState,
    SceneTransition,
    SceneNode,
    RenderLayer,
    Camera,
)

__all__ = [
    "main",
    # Event dispatcher
    "event_dispatcher",
    "get_event_dispatcher",
    "EventDispatcher",
    "EventCondition",
    "EventHandler",
    # Scene system
    "Scene",
    "TiledScene",
    "SceneManager",
    "scene_manager",
    "SceneState",
    "SceneTransition",
    "SceneNode",
    "RenderLayer",
    "Camera",
]
