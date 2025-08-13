import os
from pathlib import Path
import sys

import pygame

from apu.core.enums import Directions
from apu.core.spritesheet import AnimationSequence, SpriteSheet

# Import the correct modules
import apu.entities
import apu.font
from apu.loading import TiledMapLoader
from apu.scene import TiledScene


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

        map_sprites = TiledMapLoader().load(self._assets_path + "map.json", self._assets_path)
        self.tiled_map = TiledScene(16, *map_sprites)

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

        for tile in map_sprites:
            print(f"tile position: {tile.position}")

            for hitbox in tile.hitboxes.values():
                print(f"hitbox: {hitbox}")

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
