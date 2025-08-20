from collections.abc import Generator

import pygame
import pytest

from apu.collision import HitBox
from apu.core.enums import Directions
from apu.core.spritesheet import AnimationSequence
from apu.objects.components import AnimationComponent, MovementComponent, SolidBodyComponent
from apu.objects.entities import BaseSprite


@pytest.fixture(autouse=True)
def pygame_init() -> Generator[None, None, None]:
    pygame.init()
    yield
    pygame.quit()


def test_basesprite_creation() -> None:
    sprite = BaseSprite(position=(10, 20), layer=1)
    assert sprite.x == 10
    assert sprite.y == 20
    assert sprite._layer == 1
    assert isinstance(sprite.image, pygame.Surface)
    assert sprite.computed_rect.size == sprite.image.get_size()
    assert sprite.components == {}


def test_basesprite_add_and_get_component() -> None:
    sprite = BaseSprite(position=(0, 0))
    solid_body_component = SolidBodyComponent()
    sprite.add_component(solid_body_component)

    assert sprite.get_component(SolidBodyComponent)
    assert sprite.get_component(SolidBodyComponent) is solid_body_component
    assert sprite.get_component(MovementComponent) is None

    assert solid_body_component.entity is sprite


def test_basesprite_remove_component() -> None:
    sprite = BaseSprite(position=(0, 0))
    solid_body_component = SolidBodyComponent()
    sprite.add_component(solid_body_component)

    assert sprite.get_component(SolidBodyComponent)

    sprite.remove_component(SolidBodyComponent)

    assert not sprite.get_component(SolidBodyComponent)


def test_solidbody_component_hitbox_management() -> None:
    sprite = BaseSprite(position=(0, 0))
    rect = pygame.Rect(0, 0, 10, 10)
    hitbox = HitBox(rect)
    solid_body_component = SolidBodyComponent(box1=hitbox)

    sprite.add_component(solid_body_component)

    assert "box1" in solid_body_component.hitboxes
    assert solid_body_component.solid


def test_animation_component_management() -> None:
    sprite = BaseSprite(position=(0, 0))

    class DummyAnim(AnimationSequence):
        def __init__(self) -> None:
            dummy_surface = pygame.Surface((1, 1))
            super().__init__(frames=[dummy_surface], loop=True, frame_duration=5)

    anim_sequence = DummyAnim()
    animation_component = AnimationComponent(idle=anim_sequence)

    sprite.add_component(animation_component)

    assert "idle" in animation_component.animations
    assert animation_component.current_sequence == "idle"
    assert animation_component.get_animation_speed() == 5

    animation_component.set_animation_speed(10)
    assert animation_component.get_animation_speed() == 10

    animation_component.switch_to("idle")
    assert animation_component.current_sequence == "idle"


def test_movement_component_movement() -> None:
    sprite = BaseSprite(position=(0, 0))
    movement_component = MovementComponent(speed=2)
    sprite.add_component(movement_component)

    movement_component.move(Directions.RIGHT)
    assert Directions.RIGHT in movement_component.movements

    movement_component.stop(Directions.RIGHT)
    assert Directions.RIGHT not in movement_component.movements

    movement_component.move(Directions.DOWN, dt=2.0)
    assert Directions.DOWN in movement_component.movements

    movement_component.stop(Directions.DOWN)
    assert Directions.DOWN not in movement_component.movements
