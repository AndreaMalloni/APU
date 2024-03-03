from time import perf_counter
from enum import IntEnum
import pygame


class Directions(IntEnum):
    UP = 0
    LEFT = 1
    DOWN = 2
    RIGHT = 3


class ImageTools:
    @staticmethod
    def clip(surf: pygame.Surface, x: int, y: int, width: int, height: int) -> pygame.Surface:
        handle_surf = surf.copy()
        rect = pygame.Rect(x, y, width, height)
        handle_surf.set_clip(rect)
        image = surf.subsurface(handle_surf.get_clip())
        return image.copy()

    @staticmethod
    def palette_swap(surf: pygame.Surface, old_color: pygame.Color, new_color: pygame.Color) -> pygame.Surface:
        copy = pygame.Surface(surf.get_size())
        copy.fill(new_color)
        surf.set_colorkey(old_color)
        copy.blit(surf, (0, 0))
        return copy.convert_alpha()

    @staticmethod
    def circle_surface(radius, color):
        surf = pygame.Surface((radius * 2, radius * 2))
        pygame.draw.circle(surf, color, (radius, radius), radius)
        surf.set_colorkey((0, 0, 0))
        return surf

    @staticmethod
    def fps_surface(clock: pygame.time.Clock, font: pygame.font.Font, color: pygame.Color) -> pygame.Surface:
        fps = str(int(clock.get_fps()))
        return font.render(fps, True, color)


def delta_time(last_time: float, frame_rate: int = 60) -> tuple[float, float]:
    updated_last_time = perf_counter()
    dt = (updated_last_time - last_time) * frame_rate
    return dt, updated_last_time


def translate_rect(tmx_object):
    points = tmx_object.as_points
    left = points[0][0]
    top = points[0][1]
    width = points[3][0] - points[0][0]
    height = points[1][1] - points[0][1]
    return pygame.Rect(left, top, width, height)


if __name__ == "__main__":
    print("All imports working!")
