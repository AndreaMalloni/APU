from collections.abc import Generator
from typing import Any

import pygame
import pytest

from apu.entities import BaseSprite, MovableSprite


@pytest.fixture(autouse=True)
def pygame_init() -> Generator[None, None, None]:
    pygame.init()
    yield
    pygame.quit()


def test_basesprite_creation() -> None:
    sprite = BaseSprite(position=(10, 20), layer=1)
    assert sprite.position == (10, 20)
    assert sprite._layer == 1
    assert isinstance(sprite.image, pygame.Surface)
    assert sprite.size == sprite.image.get_size()
    assert isinstance(sprite.computed_rect, pygame.Rect)
    assert sprite.hitboxes == {}
    assert not sprite.solid


def test_basesprite_hitbox() -> None:
    sprite = BaseSprite(position=(0, 0))
    rect = pygame.Rect(0, 0, 10, 10)
    sprite.add_hitbox(box1=rect)
    assert "box1" in sprite.hitboxes
    assert sprite.solid


def test_basesprite_animation() -> None:
    sprite = BaseSprite(position=(0, 0))

    # Fake AnimationSequence for test
    class DummyAnim:
        def __iter__(self) -> Any:
            return self

        frame_duration = 5

    anim = DummyAnim()
    # Note: This will fail type checking but works at runtime
    sprite.add_animation(idle=anim)
    assert "idle" in sprite.animations
    assert sprite.current_sequence == "idle"
    assert sprite.get_animation_speed() == 5
    sprite.set_animation_speed(10)
    assert sprite.get_animation_speed() == 10
    sprite.switch_to("idle")
    assert sprite.current_sequence == "idle"


def test_movablesprite_move_and_stop() -> None:
    from apu.core.enums import Directions

    sprite = MovableSprite(position=(0, 0), speed=2)
    sprite.move(Directions.RIGHT)
    assert Directions.RIGHT in sprite.movements
    sprite.stop(Directions.RIGHT)
    assert Directions.RIGHT not in sprite.movements
    # Move with dt
    sprite.move(Directions.DOWN, dt=2.0)
    assert Directions.DOWN in sprite.movements
    sprite.stop(Directions.DOWN)
    assert Directions.DOWN not in sprite.movements
