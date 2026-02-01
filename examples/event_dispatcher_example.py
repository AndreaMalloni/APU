#!/usr/bin/env python3
"""
Esempio completo di utilizzo del nuovo sistema Event Dispatcher di APU.

Questo esempio mostra:
- Registrazione eventi con condizioni
- Sistema di priorità
- Condizioni globali
- Gestione stati del gioco
- Abilitazione/disabilitazione eventi
"""

from pathlib import Path
import sys

import pygame

# Aggiungi il path del progetto per importare APU
sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

from apu.events import EventCondition, event_dispatcher


class GameState:
    """Gestisce lo stato del gioco"""

    def __init__(self):
        self.paused = False
        self.game_over = False
        self.score = 0
        self.player_pos = [320, 240]
        self.player_speed = 5


class EventDispatcherExample:
    """Esempio completo di utilizzo del nuovo Event Dispatcher"""

    def __init__(self):
        pygame.init()
        self.screen = pygame.display.set_mode((800, 600))
        pygame.display.set_caption("APU Event Dispatcher Example")
        self.clock = pygame.time.Clock()

        self.state = GameState()
        self.font = pygame.font.Font(None, 36)

        # Setup del sistema di eventi
        self.setup_events()

    def setup_events(self):
        """Configura tutti gli eventi del gioco"""
        dispatcher = event_dispatcher()

        # Condizioni globali
        dispatcher.register_global_condition("game_not_over", lambda: not self.state.game_over)
        dispatcher.register_global_condition("game_not_paused", lambda: not self.state.paused)

        # Eventi di sistema (alta priorità)
        dispatcher.register_key_event(key=pygame.K_ESCAPE, action=self.quit_game, priority=100)

        dispatcher.register_key_event(key=pygame.K_q, action=self.quit_game, priority=100)

        # Eventi di pausa
        dispatcher.register_key_event(key=pygame.K_p, action=self.toggle_pause, priority=90)

        # Eventi di movimento (solo se il gioco non è in pausa)
        dispatcher.register_event(
            event_type=pygame.KEYDOWN,
            action=self.handle_movement,
            condition=lambda e: e.key
            in [pygame.K_UP, pygame.K_DOWN, pygame.K_LEFT, pygame.K_RIGHT],
            condition_type=EventCondition.CUSTOM,
            priority=50,
        )

        # Eventi di scoring (solo se il gioco è attivo)
        dispatcher.register_key_event(key=pygame.K_SPACE, action=self.add_score, priority=30)

        # Eventi di debug
        dispatcher.register_key_event(key=pygame.K_d, action=self.toggle_debug, priority=10)

        # Eventi di reset
        dispatcher.register_key_event(key=pygame.K_r, action=self.reset_game, priority=80)

        # Eventi di mouse (solo se il gioco è attivo)
        dispatcher.register_event(
            event_type=pygame.MOUSEBUTTONDOWN,
            action=self.handle_mouse_click,
            condition=lambda e: e.button == 1,  # Solo click sinistro
            condition_type=EventCondition.CUSTOM,
            priority=20,
        )

    def quit_game(self, event):
        """Chiude il gioco"""
        print("Uscita dal gioco...")
        pygame.quit()
        sys.exit()

    def toggle_pause(self, event):
        """Attiva/disattiva la pausa"""
        self.state.paused = not self.state.paused
        status = "PAUSATO" if self.state.paused else "RIPRESO"
        print(f"Gioco {status}")

    def handle_movement(self, event):
        """Gestisce il movimento del player"""
        if event.key == pygame.K_UP:
            self.state.player_pos[1] -= self.state.player_speed
        elif event.key == pygame.K_DOWN:
            self.state.player_pos[1] += self.state.player_speed
        elif event.key == pygame.K_LEFT:
            self.state.player_pos[0] -= self.state.player_speed
        elif event.key == pygame.K_RIGHT:
            self.state.player_pos[0] += self.state.player_speed

        # Mantieni il player dentro lo schermo
        self.state.player_pos[0] = max(0, min(800 - 20, self.state.player_pos[0]))
        self.state.player_pos[1] = max(0, min(600 - 20, self.state.player_pos[1]))

    def add_score(self, event):
        """Aggiunge punti al punteggio"""
        self.state.score += 10
        print(f"Punteggio: {self.state.score}")

    def toggle_debug(self, event):
        """Attiva/disattiva modalità debug"""
        print("Debug mode toggled")

    def reset_game(self, event):
        """Resetta il gioco"""
        self.state.score = 0
        self.state.player_pos = [320, 240]
        self.state.paused = False
        self.state.game_over = False
        print("Gioco resettato")

    def handle_mouse_click(self, event):
        """Gestisce i click del mouse"""
        print(f"Click del mouse a ({event.pos[0]}, {event.pos[1]})")

    def render(self):
        """Rende il frame corrente"""
        self.screen.fill((50, 50, 50))

        # Disegna il player
        pygame.draw.rect(
            self.screen,
            (255, 255, 0),
            (self.state.player_pos[0], self.state.player_pos[1], 20, 20),
        )

        # Testo informativo
        info_texts = [
            f"Punteggio: {self.state.score}",
            f"Posizione: ({self.state.player_pos[0]}, {self.state.player_pos[1]})",
            "Controlli:",
            "  Frecce: Muovi il player",
            "  Spazio: Aggiungi punti",
            "  P: Pausa/Riprendi",
            "  R: Reset gioco",
            "  D: Debug mode",
            "  ESC/Q: Esci",
            "  Mouse: Click per debug",
        ]

        if self.state.paused:
            info_texts.append("=== GIOCO IN PAUSA ===")

        if self.state.game_over:
            info_texts.append("=== GAME OVER ===")

        for i, text in enumerate(info_texts):
            surface = self.font.render(text, True, (255, 255, 255))
            self.screen.blit(surface, (10, 10 + i * 30))

        pygame.display.flip()

    def run(self):
        """Loop principale del gioco"""
        print("Avvio esempio Event Dispatcher...")
        print("Usa i controlli mostrati a schermo per testare le funzionalità")

        running = True
        while running:
            self.clock.tick(60)

            # Processa eventi
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    running = False
                else:
                    event_dispatcher().dispatch(event)

            # Render
            self.render()

        pygame.quit()


if __name__ == "__main__":
    example = EventDispatcherExample()
    example.run()
