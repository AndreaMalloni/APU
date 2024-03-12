import pygame

from APU.spritesheet import AnimationSequence
from APU.utility import Directions


class BaseSprite(pygame.sprite.Sprite):
    """
    Represents a generic static sprite and provides methods
    to draw itself on the (pygame) display and get the current position/size.
    """

    def __init__(self,
                 position: tuple[int, int],
                 layer: int = 0,
                 image: pygame.Surface = pygame.Surface((0, 0))) -> None:

        """Constructs a sprite object with basic functionality.

        Args:
            position (tuple): x and y coordinates of the sprite.
            layer (int, optional): the layer to draw the image to. Defaults to 0.
            image (pygame.Surface, optional): default image to draw. Defaults to empty surface.
        """
        self._layer = layer
        super(BaseSprite, self).__init__()
        self.image = image
        self.x, self.y = position[0], position[1]

    @property
    def position(self) -> tuple[int, int]:
        """Returns a vector of int values (x position, y position)."""
        return self.x, self.y

    @property
    def size(self) -> tuple[int, int]:
        """Returns a tuple of int values (width, height)."""
        return self.image.get_size()

    @property
    def rect(self) -> pygame.rect.Rect:
        return self.image.get_rect(topleft=self.position)

    def draw(self, window: pygame.Surface, flags: int = 0) -> None:
        """Draws the sprite image on the given (pygame) display in the current (x, y) position.

        Args:
            :param window: display to draw the image to.
            :param flags: pygame special_flags
        """
        window.blit(self.image, self.position, special_flags=flags)

    def update(self) -> None:
        pass


class MovableBody:
    """
    Represents a generic sprite with moving functionality that can also be animated.
    Can handle movements in 4 different directions and provides methods to move the sprite or stop it.
    """

    def __init__(self,
                 speed: int = 1,
                 acceleration: int = 0):
        super().__init__()
        self.speed = speed
        self.acceleration = acceleration
        self.is_moving = False
        self.facing_direction = Directions.DOWN

        self._delta_speed = speed
        self._state = {
            Directions.UP: [False, False],
            Directions.LEFT: [False, False],
            Directions.DOWN: [False, False],
            Directions.RIGHT: [False, False],
        }

    @property
    def movements(self) -> tuple[Directions]:
        directions = [key for key in self._state if self._state[key][0]]
        return tuple(directions)

    def start(self, direction: Directions, loop: bool = False, dt: float = 1.0):
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

    def move(self) -> tuple[float, float]:
        delta_x = ((self._state[Directions.LEFT][0] - self._state[Directions.RIGHT][0]) *
                      (self.speed + self.acceleration))
        delta_y = ((self._state[Directions.UP][0] - self._state[Directions.DOWN][0]) *
                      (self.speed + self.acceleration))

        for direction in self.movements:
            if not self._state[direction][1]:
                self.stop(direction)

        return delta_x, delta_y


class SolidBody:
    def __init__(self, **hitboxes: pygame.rect.Rect):
        super().__init__()
        self.__hitboxes = {}
        self.add_hitbox(**hitboxes)

    def add_hitbox(self, **boxes: pygame.rect.Rect) -> None:
        """Updates the hitbox dict with any given rect."""
        self.__hitboxes.update(**boxes)

    @property
    def hitboxes(self) -> dict:
        return self.__hitboxes

    @property
    def solid(self) -> bool:
        return bool(self.hitboxes)


class AnimatedBody:
    def __init__(self, fallback: pygame.Surface = pygame.Surface((0, 0)), **sequences: AnimationSequence):
        super().__init__()
        self.animations = {}
        self.current_sequence = None
        self.__fallback_image = fallback
        self.add_animation(**sequences)

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

    def play_current(self) -> pygame.Surface:
        if any(self.animations):
            try:
                return self.animations[self.current_sequence].__next__()
            except KeyError:
                return self.__fallback_image


class Entity(BaseSprite):
    def __init__(self,
                 position: tuple[int, int],
                 layer: int = 0,
                 image: pygame.Surface = pygame.Surface((0, 0)),
                 m_body: MovableBody = None,
                 s_body: SolidBody = None,
                 a_body: AnimatedBody = None):
        super().__init__(position, layer, image)
        self.movable_body = m_body
        self.solid_body = s_body
        self.animated_body = a_body

    @property
    def hitboxes(self) -> dict:
        boxes = {}

        if self.solid_body:
            for hitbox in self.solid_body.hitboxes:
                raw_box = self.solid_body.hitboxes[hitbox]
                boxes[hitbox] = pygame.rect.Rect((raw_box.x + self.x, raw_box.y + self.y),
                                                 (raw_box.width, raw_box.height))
        return boxes

    def draw(self, window: pygame.Surface, flags: int = 0) -> None:
        window.blit(self.image, self.position, special_flags=flags)

    def update(self) -> None:
        super(Entity, self).update()

        if self.movable_body.is_moving:
            delta_x, delta_y = self.movable_body.move()

            self.x -= delta_x
            self.y -= delta_y

        self.image = self.animated_body.play_current()


if __name__ == "__main__":
    print("All imports working!")
