from abc import ABC, abstractmethod
from collections import UserDict
from typing import Optional, override

from pygame.surface import Surface

from apu.collision import HitBox
from apu.core.enums import Directions
from apu.core.spritesheet import AnimationSequence


class HitBoxDict(UserDict):
    def __init__(self, body: "SolidBodyComponent", *args, **kwargs):
        self._body = body  # salvi il riferimento al componente
        super().__init__(*args, **kwargs)

    def __setitem__(self, key: str, value: "HitBox") -> None:
        value._body = self._body
        super().__setitem__(key, value)


class BaseComponent(ABC):
    def __init__(self) -> None:
        self.entity = None

    @abstractmethod
    def on_added(self) -> None:
        """Chiamato quando il componente viene aggiunto a un'entità"""

    @abstractmethod
    def on_removed(self) -> None:
        """Chiamato quando il componente viene rimosso"""

    @abstractmethod
    def update(self) -> None:
        """Aggiornamento opzionale"""

    @abstractmethod
    def draw(self, surface: Surface) -> None:
        """Render opzionale"""


class MovementComponent(BaseComponent):
    def __init__(self, speed: int = 1, acceleration: int = 0) -> None:
        super().__init__()
        self.speed = speed
        self.acceleration = acceleration
        self.is_moving = False
        self.facing_direction = Directions.DOWN

        self._delta_speed: float = float(speed)
        self._state = {
            Directions.UP: [False, False],
            Directions.LEFT: [False, False],
            Directions.DOWN: [False, False],
            Directions.RIGHT: [False, False],
        }

    @property
    def movements(self) -> tuple[Directions, ...]:
        directions = [key for key in self._state if self._state[key][0]]
        return tuple(directions)

    def move(self, direction: Directions, loop: bool = False, dt: float = 1.0) -> None:
        if direction not in self._state:
            raise AttributeError(
                f"{direction} is not a valid moving direction. Alternatives: {self._state.keys()}"
            )

        self.is_moving = True
        self._delta_speed = self.speed * dt

        if not self._state[direction][0]:
            self.facing_direction = direction
            self._state[direction] = [True, loop]

    def stop(self, direction: Directions) -> None:
        if direction not in self._state:
            raise AttributeError(
                f"Can't stop a non valid moving direction: {direction}.  \
                Alternatives: {self._state.keys()}"
            )

        if self.is_moving:
            self._state[direction] = [False, False]
            if not self.movements:
                self.is_moving = False

    @override
    def on_added(self) -> None:
        pass

    @override
    def on_removed(self) -> None:
        pass

    @override
    def update(self) -> None:
        if self.is_moving and self.entity is not None:
            x_movement = (self._state[Directions.LEFT][0] - self._state[Directions.RIGHT][0]) * (
                self.speed + self.acceleration
            )
            y_movement = (self._state[Directions.UP][0] - self._state[Directions.DOWN][0]) * (
                self.speed + self.acceleration
            )

            self.entity.x -= x_movement
            self.entity.y -= y_movement

            for direction in self.movements:
                if not self._state[direction][1]:
                    self.stop(direction)

    @override
    def draw(self, surface: Surface) -> None:
        pass


class AnimationComponent(BaseComponent):
    def __init__(self, **sequences: AnimationSequence) -> None:
        super().__init__()
        self.animations: dict[str, AnimationSequence] = {}
        self.current_sequence: Optional[str] = None

        self.add_animation(**sequences)
        self.__fallBackImage: Optional[Surface] = None

    def add_animation(self, **sequences: AnimationSequence) -> None:
        """Updates the animations dict with any given animation sequence."""
        self.animations.update(**sequences)
        if self.current_sequence is None:
            self.switch_to(next(iter(self.animations.keys())))

    def switch_to(self, animation_key: str) -> None:
        """Changes the current playing animation and calls the corresponding iter()
        method to start frame iteration

        Args:
            animation_key (str): the new animation sequence to play

        Raises:
            KeyError: if the given animationSeq does not exist
        """
        if animation_key is not None and animation_key not in self.animations:
            raise KeyError(f"This object has no assigned animation sequence named {animation_key}")

        self.current_sequence = animation_key

        if self.current_sequence is not None:
            self.animations[self.current_sequence].__iter__()

    def get_animation_speed(self, animation_key: Optional[str] = None) -> int:
        if animation_key is None:
            animation_key = self.current_sequence

        if animation_key is None:
            return 0

        return self.animations[animation_key].frame_duration

    def set_animation_speed(self, speed: int, animation_key: Optional[str] = None) -> None:
        if animation_key is None:
            animation_key = self.current_sequence

        if animation_key is None:
            return

        self.animations[animation_key].frame_duration = speed

    def pause(
        self, active: bool, animation_seq: Optional[str] = None, timer: Optional[int] = None
    ) -> None:
        """
        Pauses or resumes the animation sequence.
        """
        if animation_seq is None:
            animation_seq = self.current_sequence

        if animation_seq is None:
            return

        self.animations[animation_seq].running = active

    @override
    def on_added(self) -> None:
        self.__fallBackImage = self.entity.image

    @override
    def on_removed(self) -> None:
        pass

    @override
    def update(self) -> None:
        """
        Updates the image attribute to the next frame of the current playing animation sequence
        """

        if any(self.animations) and self.current_sequence is not None:
            try:
                self.entity.image = self.animations[self.current_sequence].__next__()
            except KeyError:
                self.image = self.__fallBackImage

    @override
    def draw(self, surface: Surface) -> None:
        pass


class SolidBodyComponent(BaseComponent):
    def __init__(self, **boxes: HitBox) -> None:
        super().__init__()
        self.hitboxes: dict[str, HitBox] = HitBoxDict(self, boxes)

    @property
    def solid(self) -> bool:
        return bool(self.hitboxes)

    def collides_with(self, other: "SolidBodyComponent") -> list[tuple[HitBox, HitBox]]:
        """
        Checks all collisions between this component's hitboxes and another's. \n
        Returns a list of tuples of all colliding hitboxes.
        """
        collisions = []

        for hitbox_a in self.hitboxes.values():
            abs_a = hitbox_a.absolute_rect(self.entity.position)
            for hitbox_b in other.hitboxes.values():
                abs_b = hitbox_b.absolute_rect(other.entity.position)
                if abs_a.colliderect(abs_b):
                    collisions.append((hitbox_a, hitbox_b))
        return collisions

    @override
    def on_added(self) -> None:
        pass

    @override
    def on_removed(self) -> None:
        pass

    @override
    def update(self) -> None:
        pass

    @override
    def draw(self, surface: Surface) -> None:
        for hitbox in self.hitboxes.values():
            hitbox.draw(surface)

    def __str__(self) -> str:
        return f"""Body component: {super().__str__()}
        Hitbox list:
        {"".join(str(hitbox) for hitbox in self.hitboxes.values())}"""

