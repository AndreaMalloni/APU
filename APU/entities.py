import copy
import abc

import pygame
from pygame import Vector2

from APU.spritesheet import AnimationSequence
from APU.utility import Directions


class Drawable(abc.ABC):
    """
    Abstract class that encapsulates the drawing operation of a (pygame) surface.

    A drawable object should contain the surface to draw and every parameter needed for its rendering, which must be
    specified as keyword arguments.
    """
    def __init__(self, **kwargs) -> None:
        self.__dict__.update(kwargs)

    @abc.abstractmethod
    def draw(self) -> None:
        """
        The object draws itself
        """
        pass



class BaseSprite(pygame.sprite.Sprite, Drawable):
    """
    Represents a generic static sprite and provides methods
    to draw itself on the (pygame) display and get the current position/size.
    """

    def __init__(self,
                 position: tuple[int, int],
                 layer: int = 0,
                 image: pygame.Surface = pygame.Surface((0, 0)),
                 rendering_flags: int = 0) -> None:
        """Constructs a sprite object with basic functionality.
 
        Args:
            position (tuple): x and y coordinates of the sprite.
            layer (int, optional): the layer to draw the image to. Defaults to 0.
            image (pygame.Surface, optional): default image to draw. Defaults to empty surface.
        """
        self._layer = layer

        Drawable.__init__(self, image=image, special_flags=rendering_flags)
        pygame.sprite.Sprite.__init__(self)
        self.x, self.y = position[0], position[1]

        self.animations = {}
        self.current_sequence = None

        self.__fallBackImage = image
        self.__hitboxes = {}

    @property
    def position(self) -> tuple:
        """Returns a vector of int values (x position, y position)."""
        return self.x, self.y

    @property
    def size(self) -> tuple[int, int]:
        """Returns a tuple of int values (width, height)."""
        return self.image.get_size()

    @property
    def rect(self) -> pygame.rect.Rect:
        return self.image.get_rect(topleft=self.position)

    @property
    def hitboxes(self) -> dict:
        boxes = {}

        for hitbox in self.__hitboxes:
            raw_box = self.__hitboxes[hitbox]
            boxes[hitbox] = pygame.rect.Rect((raw_box.x + self.x, raw_box.y + self.y),
                                             (raw_box.width, raw_box.height))
        return boxes

    @property
    def solid(self) -> bool:
        return bool(self.__hitboxes)

    def add_hitbox(self, **boxes: pygame.rect.Rect) -> None:
        """Updates the hitbox dict with any given rect."""
        self.__hitboxes.update(**boxes)

    def add_animation(self, **sequences: AnimationSequence) -> None:
        """Updates the animations dict with any given animation sequence."""
        self.animations.update(**sequences)
        if self.current_sequence is None:
            self.switch_to(list(self.animations.keys())[0])

    def switch_to(self, animation_key: str) -> None:
        """Changes the current playing animation and calls the corresponding iter()
        method to start frame iteration

        Args:
            animation_key (str): the new animation sequence to play

        Raises:
            KeyError: if the given animationSeq does not exist
        """
        if animation_key is not None and animation_key not in self.animations.keys():
            raise KeyError(f"This object has no assigned animation sequence named {animation_key}")

        self.current_sequence = animation_key
        if self.current_sequence is not None:
            self.animations[self.current_sequence].__iter__()

    def get_animation_speed(self, animation_key: str = None) -> int:
        if animation_key is None:
            animation_key = self.current_sequence

        return self.animations[animation_key].frame_duration

    def set_animation_speed(self, speed: int, animation_key: str = None) -> None:
        if animation_key is None:
            animation_key = self.current_sequence

        self.animations[animation_key].frame_duration = speed

    def pause(self, active: bool, animation_seq: str = None, timer: int = None):
        if animation_seq is None:
            animation_seq = self.current_sequence

        self.animations[animation_seq].running = active

    def draw(self, window: pygame.Surface, flags: int = 0) -> None:
        """Draws the sprite image on the given (pygame) display in the current (x, y) position.

        Args:
            :param window: display to draw the image to.
            :param flags: pygame special_flags
        """
        window.blit(self.image, self.position, special_flags=flags)

    def update(self) -> None:
        """Updates the image attribute to the next frame of the current playing animation sequence"""

        if any(self.animations):
            try:
                self.image = self.animations[self.current_sequence].__next__()
            except KeyError:
                self.image = self.__fallBackImage


class MovableSprite(BaseSprite):
    """
    Represents a generic sprite with moving functionality that can also be animated.
    Can handle movements in 4 different directions and provides methods to move the sprite or stop it.
    """

    def __init__(self,
                 position: tuple[int, int],
                 layer: int = 0,
                 image: pygame.Surface = pygame.Surface((0, 0)),
                 speed: int = 1,
                 acceleration: int = 0):

        super(MovableSprite, self).__init__(position, layer, image)
        self.speed = speed
        self.acceleration = acceleration
        self.is_moving = False
        self.facing_direction = Directions.DOWN

        self._delta_speed = speed
        self._state = {
            Directions.UP   : [False, False],
            Directions.LEFT : [False, False],
            Directions.DOWN : [False, False],
            Directions.RIGHT: [False, False],
        }

    @property
    def movements(self) -> tuple[Directions]:
        directions = [key for key in self._state if self._state[key][0]]
        return tuple(directions)

    def move(self, direction: Directions, loop: bool = False, dt: float = 1.0):
        if direction not in self._state:
            raise AttributeError(
                f"{direction} is not a valid moving direction. Alternatives: {self._state.keys()}")

        self.is_moving = True
        self._delta_speed = self.speed * dt

        if not self._state[direction][0]:
            self.facing_direction = direction
            self._state[direction] = [True, loop]

    def stop(self, direction: Directions):
        if direction not in self._state:
            raise AttributeError(
                f"Can't stop a non valid moving direction: {direction}. Alternatives: {self._state.keys()}")

        if self.is_moving:
            self._state[direction] = [False, False]
            if not self.movements:
                self.is_moving = False

    def update(self):
        if self.is_moving:
            x_movement = ((self._state[Directions.LEFT][0] - self._state[Directions.RIGHT][0]) *
                          (self.speed + self.acceleration))
            y_movement = ((self._state[Directions.UP][0] - self._state[Directions.DOWN][0]) *
                          (self.speed + self.acceleration))

            self.x -= x_movement
            self.y -= y_movement

            for direction in self.movements:
                if not self._state[direction][1]:
                    self.stop(direction)
        super(MovableSprite, self).update()


if __name__ == "__main__":
    print("All imports working!")
