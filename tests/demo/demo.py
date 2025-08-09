import json
import os
from pathlib import Path
import sys

import pygame

from apu.core.enums import Directions
from apu.core.spritesheet import AnimationSequence, SpriteSheet

# Import the correct modules
import apu.entities
import apu.font
from apu.scene import TiledScene


def load_map(map_path: str, assets_path: str) -> list[apu.entities.BaseSprite]:
    with Path(map_path).open() as f:
        json_data = json.load(f)
    tile_size = json_data["tileheight"]
    sheet = SpriteSheet(assets_path + "tileset.png")

    def get_objects() -> dict[int, pygame.Rect]:
        objects = {}
        for tileset in json_data["tilesets"]:
            for tile in tileset["tiles"]:
                if "objectgroup" in tile:
                    for obj in tile["objectgroup"]["objects"]:
                        objects[tile["id"]] = pygame.rect.Rect(
                            (obj["x"], obj["y"]), (obj["width"], obj["height"])
                        )
        return objects

    def get_animations_by_id(tile_id: int) -> list[AnimationSequence]:
        animations = []
        for tileset in json_data["tilesets"]:
            for tile in tileset["tiles"]:
                if tile["id"] == tile_id and "animation" in tile:
                    images = sheet.load_sequence(
                        pygame.rect.Rect((), (tile_size, tile_size)),
                        len(tile["animation"].values()),
                        pygame.color.Color(0, 0, 0),
                    )
                    animations.append(
                        AnimationSequence(images, True, tile["animation"][0]["duration"])
                    )
        return animations

    def get_image_by_id(tile_id: int) -> pygame.Surface:
        image_position = divmod(tile_id - 1, sheet.sheet.get_size()[0] // tile_size)
        image_position = (image_position[1] * tile_size, image_position[0] * tile_size)

        image = sheet.image_at(pygame.rect.Rect(image_position, (tile_size, tile_size)))
        image.set_colorkey((0, 0, 0))
        return image

    sprites = []
    hitboxes = get_objects()

    for layer_index, layer in enumerate(json_data["layers"]):
        for tile_index, tile_id in enumerate(layer["data"]):
            if tile_id != 0:
                image_position = divmod(tile_id - 1, sheet.sheet.get_size()[0] // tile_size)
                image_position = (image_position[1] * tile_size, image_position[0] * tile_size)

                tile_position = divmod(tile_index, json_data["width"])
                tile_position = (tile_position[1] * tile_size, tile_position[0] * tile_size)

                # tile animations

                image = sheet.image_at(pygame.rect.Rect(image_position, (tile_size, tile_size)))
                image.set_colorkey((0, 0, 0))
                sprite = apu.entities.BaseSprite(
                    position=tile_position, layer=layer_index, image=image
                )
                if tile_id - 1 in hitboxes:
                    sprite.add_hitbox(box1=hitboxes[tile_id - 1])
                sprites.append(sprite)
    return sprites


class Game:
    def __init__(self) -> None:
        pygame.init()
        self._assets_path = str(Path(__file__).parent / "assets") + os.sep
        self.screen = pygame.display.set_mode((1280, 720), flags=pygame.SCALED, vsync=1)
        self.sheet = SpriteSheet(self._assets_path + "characters.png")
        self.assets = {
            "player_idle_right": AnimationSequence(
                self.sheet.load_sequence(pygame.Rect(0, 14, 16, 19), 4, pygame.Color(0, 0, 0)),
                True,
                120,
            ),
            "player_idle_left": AnimationSequence(
                self.sheet.load_sequence(pygame.Rect(0, 14, 16, 19), 4, pygame.Color(0, 0, 0)),
                True,
                120,
            ).mirror(),
            "player_walk_right": AnimationSequence(
                self.sheet.load_sequence(pygame.Rect(0, 44, 16, 19), 4, pygame.Color(0, 0, 0)),
                True,
                120,
            ),
            "player_walk_left": AnimationSequence(
                self.sheet.load_sequence(pygame.Rect(0, 44, 16, 19), 4, pygame.Color(0, 0, 0)),
                True,
                120,
            ).mirror(),
        }

        self.virtual_display = pygame.Surface((640, 360))
        self.clock = pygame.time.Clock()
        self.font = apu.font.Font(self._assets_path + "small_font.png", pygame.Color(0, 0, 0))
        self.running = False

        self.tiled_map = TiledScene(
            16, *load_map(self._assets_path + "map.json", self._assets_path)
        )
        self.player = apu.entities.MovableSprite(
            position=(304, 164),
            speed=2,
        )
        self.player.add_animation(
            idle_right=self.assets["player_idle_right"],
            idle_left=self.assets["player_idle_left"],
            walk_right=self.assets["player_walk_right"],
            walk_left=self.assets["player_walk_left"],
        )
        self.player.add_hitbox(
            box1=pygame.rect.Rect((0, 0), (8, 16)), box2=pygame.rect.Rect((8, 0), (8, 16))
        )
        pygame.display.set_caption("APU demo game")

    def handle_events(self) -> None:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                self.running = False
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_UP:
                    self.player.move(Directions.UP, True)
                if event.key == pygame.K_DOWN:
                    self.player.move(Directions.DOWN, True)
                if event.key == pygame.K_LEFT:
                    self.player.move(Directions.LEFT, True)
                if event.key == pygame.K_RIGHT:
                    self.player.move(Directions.RIGHT, True)
                if event.key == pygame.K_f:
                    pygame.display.toggle_fullscreen()
                if event.key == pygame.K_h:
                    self.tiled_map.show_hitbox = not self.tiled_map.show_hitbox
                if event.key == pygame.K_q:
                    self.running = False
            if event.type == pygame.KEYUP:
                if event.key == pygame.K_UP:
                    self.player.stop(Directions.UP)
                if event.key == pygame.K_DOWN:
                    self.player.stop(Directions.DOWN)
                if event.key == pygame.K_LEFT:
                    self.player.stop(Directions.LEFT)
                if event.key == pygame.K_RIGHT:
                    self.player.stop(Directions.RIGHT)

    def handle_rendering(self) -> None:
        self.virtual_display.fill((28, 17, 23))

        self.tiled_map.render(self.virtual_display)
        self.player.draw(self.virtual_display)
        self.font.render(self.virtual_display, str(int(self.clock.get_fps())), (5, 5))
        self.font.render(self.virtual_display, "Press 'f' to toggle fullscreen", (522, 5))
        self.font.render(self.virtual_display, "Press 'h' to toggle hitboxes", (522, 15))
        self.font.render(self.virtual_display, "Press 'q' to quit", (522, 25))
        self.screen.blit(
            pygame.transform.scale(self.virtual_display, self.screen.get_size()), (0, 0)
        )

    def update_state(self) -> None:
        if not self.player.is_moving:
            if (
                self.player.facing_direction == Directions.LEFT
                and self.player.current_sequence != "idle_left"
            ):
                self.player.switch_to("idle_left")
            if (
                self.player.facing_direction == Directions.RIGHT
                and self.player.current_sequence != "idle_right"
            ):
                self.player.switch_to("idle_right")
        else:
            if (
                self.player.facing_direction == Directions.LEFT
                and self.player.current_sequence != "walk_left"
            ):
                self.player.switch_to("walk_left")
            if (
                self.player.facing_direction == Directions.RIGHT
                and self.player.current_sequence != "walk_right"
            ):
                self.player.switch_to("walk_right")
        self.player.update()

    def run(self) -> None:
        self.running = not self.running

        while self.running:
            self.clock.tick(2000)
            self.handle_events()
            self.handle_rendering()
            self.update_state()
            pygame.display.update()

        sys.exit()


if __name__ == "__main__":
    Game().run()
