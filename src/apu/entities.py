from typing import Optional, cast

import pygame
from typing_extensions import override

from apu.core.enums import Directions
from apu.core.spritesheet import AnimationSequence


class BaseSprite(pygame.sprite.Sprite):
    """
    Represents a generic static sprite and provides methods
    to draw itself on the (pygame) display and get the current position/size.
    """

    def __init__(
        self, position: tuple[int, int], layer: int = 0, image: Optional[pygame.Surface] = None
    ) -> None:
        """Constructs a sprite object with basic functionality.

        Args:
            position (tuple): x and y coordinates of the sprite.
            layer (int, optional): the layer to draw the image to. Defaults to 0.
            image (pygame.Surface, optional): default image to draw. Defaults to empty surface.
        """
        self._layer = layer
        super().__init__()
        self.image = image if image is not None else pygame.Surface((0, 0))
        self.x: int = position[0]
        self.y: int = position[1]

        self.animations: dict[str, object] = {}
        self.current_sequence: Optional[str] = None

        self.__fallBackImage = image
        self.__hitboxes: dict[str, pygame.Rect] = {}

    @property
    def position(self) -> tuple[int, int]:
        """Returns a vector of int values (x position, y position)."""
        return self.x, self.y

    @property
    def size(self) -> tuple[int, int]:
        """Returns a tuple of int values (width, height)."""
        if self.image is not None:
            size: tuple[int, int] = self.image.get_size()
            return (size[0], size[1])
        return (0, 0)

    @property
    def computed_rect(self) -> pygame.rect.Rect:
        if self.image is not None:
            return self.image.get_rect(topleft=self.position)
        return pygame.Rect(self.position, (0, 0))

    @property
    def hitboxes(self) -> dict[str, pygame.Rect]:
        boxes = {}

        for hitbox in self.__hitboxes:
            raw_box = self.__hitboxes[hitbox]
            boxes[hitbox] = pygame.rect.Rect(
                (raw_box.x + self.x, raw_box.y + self.y), (raw_box.width, raw_box.height)
            )
        return boxes

    @property
    def solid(self) -> bool:
        return bool(self.__hitboxes)

    def add_hitbox(self, **boxes: pygame.rect.Rect) -> None:
        """Updates the hitbox dict with any given rect."""
        self.__hitboxes.update(**boxes)

    def add_animation(self, **sequences: object) -> None:
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
            anim = cast(AnimationSequence, self.animations[self.current_sequence])
            anim.__iter__()

    def get_animation_speed(self, animation_key: Optional[str] = None) -> int:
        if animation_key is None:
            animation_key = self.current_sequence
        if animation_key is None:
            return 0

        anim = cast(AnimationSequence, self.animations[animation_key])
        return anim.frame_duration

    def set_animation_speed(self, speed: int, animation_key: Optional[str] = None) -> None:
        if animation_key is None:
            animation_key = self.current_sequence
        if animation_key is None:
            return

        anim = cast(AnimationSequence, self.animations[animation_key])
        anim.frame_duration = speed

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

        anim = cast(AnimationSequence, self.animations[animation_seq])
        anim.running = active

    def draw(self, window: pygame.Surface, flags: int = 0) -> None:
        """
        Draws the sprite image on the given (pygame) display in the current (x, y) position.

        Args:
            :param window: display to draw the image to.
            :param flags: pygame special_flags
        """
        if self.image is not None:
            window.blit(self.image, self.position, special_flags=flags)

    @override
    def update(self) -> None:
        """
        Updates the image attribute to the next frame of the current playing animation sequence
        """

        if any(self.animations) and self.current_sequence is not None:
            try:
                anim = cast(AnimationSequence, self.animations[self.current_sequence])
                self.image = anim.__next__()
            except KeyError:
                self.image = self.__fallBackImage


class MovableSprite(BaseSprite):
    """
    Represents a generic sprite with moving functionality that can also be animated.
    Can handle movements in 4 different directions and provides methods to move or stop the sprite.
    """

    def __init__(
        self,
        position: tuple[int, int],
        layer: int = 0,
        image: Optional[pygame.Surface] = None,
        speed: int = 1,
        acceleration: int = 0,
    ) -> None:
        super().__init__(position, layer, image)
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
    def update(self) -> None:
        if self.is_moving:
            x_movement = (self._state[Directions.LEFT][0] - self._state[Directions.RIGHT][0]) * (
                self.speed + self.acceleration
            )
            y_movement = (self._state[Directions.UP][0] - self._state[Directions.DOWN][0]) * (
                self.speed + self.acceleration
            )

            self.x -= x_movement
            self.y -= y_movement

            for direction in self.movements:
                if not self._state[direction][1]:
                    self.stop(direction)
        super().update()


if __name__ == "__main__":
    print("All imports working!")
