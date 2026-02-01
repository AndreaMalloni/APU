#!/usr/bin/env python3
"""
Esempio completo della nuova architettura di Scene di APU con Eventi Pygame Personalizzati.

Questo esempio mostra:
- Eventi pygame personalizzati per le scene
- Sistema unificato di gestione eventi
- Gerarchia di scene
- SceneManager con stack di scene
- Layer di rendering
- Camera e transizioni
- Scene personalizzate
"""

import math
from pathlib import Path
import sys

import pygame

# Aggiungi il path del progetto per importare APU
sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

from apu.events import event_dispatcher
from apu.scene import (
    SCENE_CUSTOM,
    SCENE_ENTER,
    SCENE_EXIT,
    SCENE_PAUSE,
    SCENE_RESUME,
    Camera,
    RenderLayer,
    Scene,
    scene_manager,
)


class MenuScene(Scene[pygame.Surface]):
    """Scena di menu con UI"""

    def __init__(self, name: str = "menu"):
        super().__init__(name)
        self.font = pygame.font.Font(None, 48)
        self.selected_option = 0
        self.options = ["Play Game", "Settings", "Quit"]
        self.background_color = (50, 50, 100)

    def update(self, dt: float):
        super().update(dt)
        # Logica del menu (se necessario)

    def render(self, surface: pygame.Surface, camera: Camera | None = None):
        # Sfondo
        surface.fill(self.background_color)

        # Titolo
        title = self.font.render("APU Scene Demo", True, (255, 255, 255))
        title_rect = title.get_rect(center=(surface.get_width() // 2, 100))
        surface.blit(title, title_rect)

        # Opzioni del menu
        for i, option in enumerate(self.options):
            color = (255, 255, 0) if i == self.selected_option else (255, 255, 255)
            text = self.font.render(option, True, color)
            text_rect = text.get_rect(center=(surface.get_width() // 2, 250 + i * 60))
            surface.blit(text, text_rect)

        # Istruzioni
        small_font = pygame.font.Font(None, 24)
        instructions = [
            "Use UP/DOWN arrows to navigate",
            "Press ENTER to select",
            "Press ESC to go back",
        ]
        for i, instruction in enumerate(instructions):
            text = small_font.render(instruction, True, (200, 200, 200))
            surface.blit(text, (20, surface.get_height() - 80 + i * 25))


class GameScene(Scene[pygame.Rect]):
    """Scena di gioco con elementi animati"""

    def __init__(self, name: str = "game"):
        camera = Camera(position=(0, 0), zoom=1.0)
        super().__init__(name, camera)

        # Crea elementi di gioco
        self.create_game_elements()

        # Aggiungi handler per il rendering personalizzato
        self.add_render_handler(self.render_particles)

    def create_game_elements(self):
        """Crea elementi di gioco per layer diversi"""

        # Background elements
        for i in range(5):
            rect = pygame.Rect(i * 150, 50, 100, 100)
            self.add_item(rect, RenderLayer.BACKGROUND)

        # Terrain elements
        for i in range(8):
            rect = pygame.Rect(i * 100, 200, 80, 80)
            self.add_item(rect, RenderLayer.TERRAIN)

        # Entity elements
        for i in range(3):
            rect = pygame.Rect(100 + i * 120, 300, 60, 60)
            self.add_item(rect, RenderLayer.ENTITIES)

        # UI elements
        ui_rect = pygame.Rect(10, 10, 200, 50)
        self.add_item(ui_rect, RenderLayer.UI)

        # Custom layer
        custom_rect = pygame.Rect(400, 100, 50, 50)
        self.add_item(custom_rect, "effects")

    def render_particles(self, surface: pygame.Surface, camera: Camera):
        """Handler personalizzato per particelle"""
        # Simula particelle
        for i in range(10):
            x = 300 + math.sin(pygame.time.get_ticks() * 0.001 + i) * 50
            y = 150 + math.cos(pygame.time.get_ticks() * 0.001 + i) * 30
            pygame.draw.circle(surface, (255, 255, 0), (int(x), int(y)), 3)

    def update(self, dt: float):
        super().update(dt)

        # Anima gli elementi
        for item in self.get_items(RenderLayer.ENTITIES):
            item.x += math.sin(pygame.time.get_ticks() * 0.001) * 2 * dt
            item.y += math.cos(pygame.time.get_ticks() * 0.002) * 1 * dt

    def render(self, surface: pygame.Surface, camera: Camera | None = None):
        super().render(surface, camera)

        # Rendi gli elementi per layer
        for layer in RenderLayer:
            items = self.get_items(layer)
            for item in items:
                color = self.get_layer_color(layer)
                pygame.draw.rect(surface, color, item, 2)

        # Rendi layer custom
        for item in self.get_items("effects"):
            pygame.draw.circle(surface, (255, 0, 255), item.center, 10)

    def get_layer_color(self, layer: RenderLayer):
        """Ottiene il colore per un layer"""
        colors = {
            RenderLayer.BACKGROUND: (100, 100, 100),
            RenderLayer.TERRAIN: (150, 75, 0),
            RenderLayer.DECORATIONS: (0, 150, 0),
            RenderLayer.ENTITIES: (0, 0, 255),
            RenderLayer.UI: (255, 0, 0),
            RenderLayer.OVERLAY: (255, 255, 0),
        }
        return colors.get(layer, (255, 255, 255))


class SettingsScene(Scene[str]):
    """Scena delle impostazioni"""

    def __init__(self, name: str = "settings"):
        super().__init__(name)
        self.font = pygame.font.Font(None, 36)
        self.settings = {
            "Music Volume": 50,
            "Sound Effects": 75,
            "Graphics Quality": "High",
            "Fullscreen": False,
        }
        self.selected_setting = 0

    def update(self, dt: float):
        super().update(dt)

    def render(self, surface: pygame.Surface, camera: Camera | None = None):
        surface.fill((30, 30, 50))

        # Titolo
        title = self.font.render("Settings", True, (255, 255, 255))
        title_rect = title.get_rect(center=(surface.get_width() // 2, 50))
        surface.blit(title, title_rect)

        # Impostazioni
        settings_list = list(self.settings.items())
        for i, (key, value) in enumerate(settings_list):
            color = (255, 255, 0) if i == self.selected_setting else (255, 255, 255)
            text = f"{key}: {value}"
            text_surface = self.font.render(text, True, color)
            text_rect = text_surface.get_rect(center=(surface.get_width() // 2, 150 + i * 50))
            surface.blit(text_surface, text_rect)


class SceneArchitectureExample:
    """Esempio principale dell'architettura di scene con eventi pygame personalizzati"""

    def __init__(self):
        pygame.init()
        self.screen = pygame.display.set_mode((800, 600))
        pygame.display.set_caption("APU Scene Architecture Example - Pygame Events")
        self.clock = pygame.time.Clock()

        # Crea le scene
        self.menu_scene = MenuScene()
        self.game_scene = GameScene()
        self.settings_scene = SettingsScene()

        # Registra le scene nel manager
        manager = scene_manager()
        manager.register_scene(self.menu_scene)
        manager.register_scene(self.game_scene)
        manager.register_scene(self.settings_scene)

        # Inizia con il menu
        manager.switch_scene("menu")

        # Setup eventi unificati
        self.setup_unified_events()

    def setup_unified_events(self):
        """Configura gli eventi unificati (pygame + scene)"""

        # Eventi pygame per navigazione
        event_dispatcher().register_key_event(key=pygame.K_UP, action=self.navigate_menu_up)

        event_dispatcher().register_key_event(key=pygame.K_DOWN, action=self.navigate_menu_down)

        event_dispatcher().register_key_event(key=pygame.K_RETURN, action=self.select_menu_option)

        event_dispatcher().register_key_event(key=pygame.K_ESCAPE, action=self.go_back)

        event_dispatcher().register_key_event(key=pygame.K_g, action=self.toggle_game_scene)

        event_dispatcher().register_key_event(key=pygame.K_s, action=self.toggle_settings_scene)

        # Eventi di scena come eventi pygame personalizzati
        event_dispatcher().register_event(
            event_type=SCENE_ENTER, action=self.on_scene_enter, priority=10
        )

        event_dispatcher().register_event(
            event_type=SCENE_EXIT, action=self.on_scene_exit, priority=10
        )

        event_dispatcher().register_event(
            event_type=SCENE_PAUSE, action=self.on_scene_pause, priority=5
        )

        event_dispatcher().register_event(
            event_type=SCENE_RESUME, action=self.on_scene_resume, priority=5
        )

        # Eventi personalizzati di scena
        event_dispatcher().register_event(
            event_type=SCENE_CUSTOM, action=self.on_scene_custom_event, priority=5
        )

    def navigate_menu_up(self, event):
        """Naviga verso l'alto nel menu"""
        active_scene = scene_manager().get_active_scene()
        if isinstance(active_scene, MenuScene):
            active_scene.selected_option = (active_scene.selected_option - 1) % len(
                active_scene.options
            )
        elif isinstance(active_scene, SettingsScene):
            active_scene.selected_setting = (active_scene.selected_setting - 1) % len(
                active_scene.settings
            )

    def navigate_menu_down(self, event):
        """Naviga verso il basso nel menu"""
        active_scene = scene_manager().get_active_scene()
        if isinstance(active_scene, MenuScene):
            active_scene.selected_option = (active_scene.selected_option + 1) % len(
                active_scene.options
            )
        elif isinstance(active_scene, SettingsScene):
            active_scene.selected_setting = (active_scene.selected_setting + 1) % len(
                active_scene.settings
            )

    def select_menu_option(self, event):
        """Seleziona un'opzione del menu"""
        active_scene = scene_manager().get_active_scene()
        if isinstance(active_scene, MenuScene):
            if active_scene.selected_option == 0:  # Play Game
                scene_manager().push_scene("game", {"from_menu": True})
            elif active_scene.selected_option == 1:  # Settings
                scene_manager().push_scene("settings")
            elif active_scene.selected_option == 2:  # Quit
                pygame.quit()
                sys.exit()

    def go_back(self, event):
        """Torna indietro"""
        scene_manager().pop_scene()

    def toggle_game_scene(self, event):
        """Attiva/disattiva la scena di gioco"""
        active_scene = scene_manager().get_active_scene()
        if active_scene.name == "game":
            scene_manager().pop_scene()
        else:
            scene_manager().push_scene("game")

    def toggle_settings_scene(self, event):
        """Attiva/disattiva la scena delle impostazioni"""
        active_scene = scene_manager().get_active_scene()
        if active_scene.name == "settings":
            scene_manager().pop_scene()
        else:
            scene_manager().push_scene("settings")

    # Handler per eventi di scena (eventi pygame personalizzati)
    def on_scene_enter(self, event):
        """Handler per evento di entrata in scena"""
        scene_name = event.scene_name
        data = event.data
        print(f"🎬 Scena '{scene_name}' entrata con dati: {data}")

    def on_scene_exit(self, event):
        """Handler per evento di uscita da scena"""
        scene_name = event.scene_name
        print(f"🚪 Scena '{scene_name}' uscita")

    def on_scene_pause(self, event):
        """Handler per evento di pausa scena"""
        scene_name = event.scene_name
        print(f"⏸️ Scena '{scene_name}' messa in pausa")

    def on_scene_resume(self, event):
        """Handler per evento di ripresa scena"""
        scene_name = event.scene_name
        print(f"▶️ Scena '{scene_name}' ripresa")

    def on_scene_custom_event(self, event):
        """Handler per eventi personalizzati di scena"""
        scene_name = event.scene_name
        event_type = event.event_type
        data = event.data
        print(
            f"🎯 Evento personalizzato '{event_type}' nella scena '{scene_name}' con dati: {data}"
        )

    def render_info(self):
        """Rende informazioni sullo stato delle scene e eventi"""
        font = pygame.font.Font(None, 24)

        # Informazioni sulla scena attiva
        active_scene = scene_manager().get_active_scene()
        scene_info = f"Active Scene: {active_scene.name if active_scene else 'None'}"
        text = font.render(scene_info, True, (255, 255, 255))
        self.screen.blit(text, (10, 10))

        # Stack delle scene
        stack_info = f"Scene Stack: {len(scene_manager()._scene_stack)} scenes"
        text = font.render(stack_info, True, (255, 255, 255))
        self.screen.blit(text, (10, 30))

        # Eventi registrati
        pygame_events = len(event_dispatcher().get_registered_events())
        events_info = f"Events: {pygame_events} pygame events (unified)"
        text = font.render(events_info, True, (255, 255, 255))
        self.screen.blit(text, (10, 50))

        # Controlli
        controls = [
            "Controls:",
            "  UP/DOWN: Navigate",
            "  ENTER: Select",
            "  ESC: Go back",
            "  G: Toggle game scene",
            "  S: Toggle settings scene",
        ]

        for i, control in enumerate(controls):
            text = font.render(control, True, (200, 200, 200))
            self.screen.blit(text, (10, 550 + i * 20))

    def run(self):
        """Loop principale"""
        print("🎮 Avvio esempio architettura Scene con Eventi Pygame Personalizzati...")
        print("📋 Usa i controlli mostrati a schermo per navigare")
        print("🔔 Gli eventi di scena verranno mostrati nella console")
        print("🎯 Tutti gli eventi (pygame + scene) sono gestiti dallo stesso sistema!")

        running = True
        while running:
            dt = self.clock.tick(60) / 1000.0

            # Processa eventi pygame (inclusi quelli personalizzati per le scene)
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    running = False
                else:
                    # Tutti gli eventi passano attraverso l'Event Dispatcher unificato
                    event_dispatcher().dispatch(event)

            # Aggiorna
            scene_manager().update(dt)

            # Render
            scene_manager().render(self.screen)
            self.render_info()

            pygame.display.flip()

        pygame.quit()


if __name__ == "__main__":
    example = SceneArchitectureExample()
    example.run()
