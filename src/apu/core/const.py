import pygame

__all__ = [
    "NEIGHBOUR_MATRIX",
    "SCENE_CUSTOM",
    "SCENE_ENTER",
    "SCENE_EVENT_TYPES",
    "SCENE_EXIT",
    "SCENE_PAUSE",
    "SCENE_RESUME",
]

NEIGHBOUR_MATRIX = [(-1, 0), (-1, -1), (0, -1), (1, -1), (1, 0), (1, 1), (0, 1), (-1, 1)]

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

