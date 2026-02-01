from enum import Enum, IntEnum, auto

__all__ = [
    "Directions",
    "EventCondition",
    "RenderLayer",
    "SceneState",
]


class Directions(IntEnum):
    UP = 0
    LEFT = 1
    DOWN = 2
    RIGHT = 3


class EventCondition(Enum):
    """Predefined conditions for events"""

    ALWAYS = auto()
    KEY_PRESSED = auto()
    KEY_RELEASED = auto()
    MOUSE_IN_AREA = auto()
    GAME_STATE_ACTIVE = auto()
    CUSTOM = auto()


class SceneState(Enum):
    """Possible states of a scene"""

    INACTIVE = auto()
    LOADING = auto()
    ACTIVE = auto()
    PAUSED = auto()
    TRANSITIONING = auto()
    UNLOADING = auto()


class RenderLayer(Enum):
    """Predefined rendering layers"""

    BACKGROUND = auto()
    TERRAIN = auto()
    DECORATIONS = auto()
    ENTITIES = auto()
    UI = auto()
    OVERLAY = auto()
