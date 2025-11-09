def main() -> None:
    print("Hello from apu!")

# Esportazioni per il sistema di event dispatcher
from apu.events import (
    EventCondition,
    EventDispatcher,
    EventHandler,
    event_dispatcher,
    get_event_dispatcher,
)

# Esportazioni per il sistema di scene
from apu.scene import (
    Camera,
    RenderLayer,
    Scene,
    SceneManager,
    SceneNode,
    SceneState,
    SceneTransition,
    TiledScene,
    scene_manager,
)

__all__ = [
    "Camera",
    "EventCondition",
    "EventDispatcher",
    "EventHandler",
    "RenderLayer",
    # Scene system
    "Scene",
    "SceneManager",
    "SceneNode",
    "SceneState",
    "SceneTransition",
    "TiledScene",
    # Event dispatcher
    "event_dispatcher",
    "get_event_dispatcher",
    "main",
    "scene_manager"
]
