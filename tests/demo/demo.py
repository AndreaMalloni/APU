import os
from pathlib import Path
import sys

import pygame

from apu.camera import Camera
from apu.collision import HitBox
from apu.core.enums import Directions, EventCondition
from apu.core.spritesheet import AnimationSequence, SpriteSheet
from apu.events import event_dispatcher
import apu.font
from apu.loading import TiledMapLoader
from apu.objects.components import AnimationComponent, MovementComponent, SolidBodyComponent
import apu.objects.entities
from apu.scene import TiledScene, scene_manager


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
        self.game_paused = False

        map_sprites = TiledMapLoader().load(self._assets_path + "map.json", self._assets_path)

        # Crea la camera
        self.camera = Camera(position=(0, 0), zoom=1.0)

        # Crea la scena tile-based con la nuova architettura
        self.tiled_map = TiledScene("main_level", 16, camera=self.camera)
        self.tiled_map.insert(*map_sprites)

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

        # Registra la scena nel manager
        scene_manager().register_scene(self.tiled_map)
        scene_manager().switch_scene("main_level")

        # Registrazione eventi con il nuovo sistema
        self._setup_events()

        pygame.display.set_caption("APU demo game")

    def _setup_events(self) -> None:
        """Configura tutti gli eventi del gioco usando il nuovo sistema"""

        # Condizione globale: il gioco deve essere attivo
        def game_active_condition() -> bool:
            return not self.game_paused

        # event_dispatcher().register_global_condition("game_active", game_active_condition)

        # Evento di chiusura (solo quando si preme 'q')
        event_dispatcher().register_key_event(
            key=pygame.K_q,
            action=self.on_quit,
            priority=10,  # Alta priorità
        )

        # Toggle fullscreen (solo quando si preme 'f')
        event_dispatcher().register_key_event(key=pygame.K_f, action=self.toggle_fullscreen)

        # Toggle hitbox (solo quando si preme 'h')
        event_dispatcher().register_key_event(key=pygame.K_h, action=self.toggle_hitbox)

        # Pausa gioco (solo quando si preme 'p')
        event_dispatcher().register_key_event(key=pygame.K_p, action=self.toggle_pause)

        # Eventi di movimento del player (solo quando il gioco è attivo)
        event_dispatcher().register_event(
            event_type=pygame.KEYDOWN,
            action=self.player.on_keydown,
            condition=lambda event: event.key
            in [pygame.K_UP, pygame.K_DOWN, pygame.K_LEFT, pygame.K_RIGHT],
            condition_type=EventCondition.CUSTOM,
            priority=5,
        )

        event_dispatcher().register_event(
            event_type=pygame.KEYUP,
            action=self.player.on_keyup,
            condition=lambda event: event.key
            in [pygame.K_UP, pygame.K_DOWN, pygame.K_LEFT, pygame.K_RIGHT],
            condition_type=EventCondition.CUSTOM,
            priority=5,
        )

    def handle_rendering(self) -> None:
        self.virtual_display.fill((28, 17, 23))

        # Usa il SceneManager per il rendering
        scene_manager().render(self.virtual_display)

        self.font.render(self.virtual_display, str(int(self.clock.get_fps())), (5, 5))
        self.font.render(self.virtual_display, "Press 'f' to toggle fullscreen", (522, 5))
        self.font.render(self.virtual_display, "Press 'h' to toggle hitboxes", (522, 15))
        self.font.render(self.virtual_display, "Press 'p' to pause/resume", (522, 25))
        self.font.render(self.virtual_display, "Press 'q' to quit", (522, 35))

        if self.game_paused:
            self.font.render(self.virtual_display, "PAUSED", (280, 160))

        self.screen.blit(
            pygame.transform.scale(self.virtual_display, self.screen.get_size()), (0, 0)
        )

    def on_quit(self, event: pygame.event.Event) -> None:
        self.running = False

    def toggle_hitbox(self, event: pygame.event.Event) -> None:
        for sprite in self.tiled_map:
            if hasattr(sprite, "hitboxes"):
                for hitbox in sprite.hitboxes.values():
                    hitbox.visible = not hitbox.visible

    def toggle_fullscreen(self, event: pygame.event.Event) -> None:
        pygame.display.toggle_fullscreen()

    def toggle_pause(self, event: pygame.event.Event) -> None:
        self.game_paused = not self.game_paused

    def run(self) -> None:
        self.running = not self.running

        while self.running:
            dt = self.clock.tick(2000) / 1000.0  # Delta time in secondi

            for event in pygame.event.get():
                event_dispatcher().dispatch(event)

            self.handle_rendering()

            # Aggiorna solo se il gioco non è in pausa
            if not self.game_paused:
                # Fai seguire la camera al player (centrata sullo schermo)
                player_center_x = self.player.x + self.player.size[0] / 2
                player_center_y = self.player.y + self.player.size[1] / 2
                screen_center_x = self.virtual_display.get_width() / 2
                screen_center_y = self.virtual_display.get_height() / 2
                target_x = player_center_x - screen_center_x
                target_y = player_center_y - screen_center_y
                self.camera.follow((target_x, target_y), dt)
                
                scene_manager().update(dt)

            pygame.display.update()

        sys.exit()


if __name__ == "__main__":
    Game().run()
