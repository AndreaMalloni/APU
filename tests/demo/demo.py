import os
from pathlib import Path
import sys

import pygame

from apu.collision import HitBox
from apu.core.enums import Directions
from apu.core.spritesheet import AnimationSequence, SpriteSheet
from apu.events.dispatcher import __EventDispatcher__
import apu.font
from apu.loading import TiledMapLoader
from apu.objects.components import AnimationComponent, MovementComponent, SolidBodyComponent
import apu.objects.entities
from apu.scene import TiledScene


class Player(apu.objects.entities.BaseSprite):
    def __init__(
        self, position: tuple[int, int], layer: int = 0, image: pygame.Surface | None = None
    ) -> None:
        super().__init__(position, layer, image)

    def on_keydown(self, event: pygame.event.Event) -> None:
        movement_comp = self.get_component(MovementComponent)
        if not movement_comp:
            return

        if event.key == pygame.K_UP:
            self.move(Directions.UP, True)
            # self.switch_to("walk_right"
            #   if self.facing_direction == Directions.RIGHT else "walk_left")
        elif event.key == pygame.K_DOWN:
            self.move(Directions.DOWN, True)
            # self.switch_to("walk_right"
            #   if self.facing_direction == Directions.RIGHT else "walk_left")
        elif event.key == pygame.K_LEFT:
            self.move(Directions.LEFT, True)
            self.switch_to("walk_left")
        elif event.key == pygame.K_RIGHT:
            self.move(Directions.RIGHT, True)
            self.switch_to("walk_right")

    def on_keyup(self, event: pygame.event.Event) -> None:
        movement_comp = self.get_component(MovementComponent)
        if not movement_comp:
            return

        if event.key == pygame.K_UP:
            self.stop(Directions.UP)
            # self.switch_to("idle_right"
            #   if self.facing_direction == Directions.RIGHT else "idle_left")
        elif event.key == pygame.K_DOWN:
            self.stop(Directions.DOWN)
            # self.switch_to("idle_right"
            #   if self.facing_direction == Directions.RIGHT else "idle_left")
        elif event.key == pygame.K_LEFT:
            self.stop(Directions.LEFT)
            self.switch_to("idle_left")
        elif event.key == pygame.K_RIGHT:
            self.stop(Directions.RIGHT)
            self.switch_to("idle_right")


class Game:
    def __init__(self) -> None:
        pygame.init()
        self._assets_path = str(Path(__file__).parent / "assets") + os.sep
        self.screen = pygame.display.set_mode((1280, 720), flags=pygame.SCALED, vsync=1)

        self.player_sheet = SpriteSheet(self._assets_path + "characters.png")
        self.assets = {
            "player_idle_right": AnimationSequence(
                self.player_sheet.load_sequence(
                    pygame.Rect(0, 14, 16, 19), 4, pygame.Color(0, 0, 0)
                ),
                True,
                120,
            ),
            "player_idle_left": AnimationSequence(
                self.player_sheet.load_sequence(
                    pygame.Rect(0, 14, 16, 19), 4, pygame.Color(0, 0, 0)
                ),
                True,
                120,
            ).mirror(),
            "player_walk_right": AnimationSequence(
                self.player_sheet.load_sequence(
                    pygame.Rect(0, 44, 16, 19), 4, pygame.Color(0, 0, 0)
                ),
                True,
                120,
            ),
            "player_walk_left": AnimationSequence(
                self.player_sheet.load_sequence(
                    pygame.Rect(0, 44, 16, 19), 4, pygame.Color(0, 0, 0)
                ),
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

        self.player = Player(position=(304, 164))
        self.player.add_component(MovementComponent(speed=2))
        self.player.add_component(
            AnimationComponent(
                idle_right=self.assets["player_idle_right"],
                idle_left=self.assets["player_idle_left"],
                walk_right=self.assets["player_walk_right"],
                walk_left=self.assets["player_walk_left"],
            )
        )
        self.player.add_component(
            SolidBodyComponent(
                box1=HitBox(pygame.rect.Rect((0, 0), (8, 16))),
                box2=HitBox(pygame.rect.Rect((8, 0), (8, 16))),
            )
        )

        self.tiled_map.insert(self.player)

        __EventDispatcher__.subscribe(pygame.QUIT, self.on_quit)
        __EventDispatcher__.subscribe(pygame.KEYDOWN, self.on_quit)
        __EventDispatcher__.subscribe(pygame.KEYDOWN, self.toggle_fullscreen)
        __EventDispatcher__.subscribe(pygame.KEYDOWN, self.toggle_hitbox)
        __EventDispatcher__.subscribe(pygame.KEYDOWN, self.player.on_keydown)
        __EventDispatcher__.subscribe(pygame.KEYUP, self.player.on_keyup)

        pygame.display.set_caption("APU demo game")

    def handle_rendering(self) -> None:
        self.virtual_display.fill((28, 17, 23))

        self.tiled_map.render(self.virtual_display)
        self.font.render(self.virtual_display, str(int(self.clock.get_fps())), (5, 5))
        self.font.render(self.virtual_display, "Press 'f' to toggle fullscreen", (522, 5))
        self.font.render(self.virtual_display, "Press 'h' to toggle hitboxes", (522, 15))
        self.font.render(self.virtual_display, "Press 'q' to quit", (522, 25))
        self.screen.blit(
            pygame.transform.scale(self.virtual_display, self.screen.get_size()), (0, 0)
        )

    def on_quit(self, event: pygame.event.Event) -> None:
        if event.key == pygame.K_q:
            self.running = False

    def toggle_hitbox(self, event: pygame.event.Event) -> None:
        if event.key == pygame.K_h:
            for sprite in self.tiled_map:
                if hasattr(sprite, "hitboxes"):
                    for hitbox in sprite.hitboxes.values():
                        hitbox.visible = not hitbox.visible

    def toggle_fullscreen(self, event: pygame.event.Event) -> None:
        if event.key == pygame.K_f:
            pygame.display.toggle_fullscreen()

    def run(self) -> None:
        self.running = not self.running

        while self.running:
            self.clock.tick(2000)

            for event in pygame.event.get():
                apu.events.dispatcher.__EventDispatcher__.dispatch(event)

            self.handle_rendering()
            self.tiled_map.update()
            pygame.display.update()

        sys.exit()


if __name__ == "__main__":
    Game().run()
