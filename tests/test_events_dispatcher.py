from unittest.mock import Mock

import pygame
import pytest

from apu.events.dispatcher import event_dispatcher
from apu.scene import (
    SCENE_CUSTOM,
    SCENE_ENTER,
    SCENE_EXIT,
    SCENE_PAUSE,
    SCENE_RESUME,
    Scene,
    scene_manager,
)


class TestEventDispatcher:
    """Test per l'EventDispatcher con eventi pygame personalizzati"""

    def setup_method(self) -> None:
        pygame.init()
        # Reset del dispatcher per ogni test
        dispatcher = event_dispatcher()
        dispatcher.clear_all_events()

    def teardown_method(self) -> None:
        pygame.quit()

    def test_event_registration(self) -> None:
        """Test registrazione eventi pygame personalizzati"""
        dispatcher = event_dispatcher()
        mock_handler = Mock()

        # Registra evento di scena come evento pygame personalizzato
        dispatcher.register_event(SCENE_ENTER, mock_handler)

        # Verifica che sia registrato
        events = dispatcher.get_registered_events()
        assert SCENE_ENTER in events
        assert len(events[SCENE_ENTER]) == 1
        assert events[SCENE_ENTER][0].action == mock_handler

    def test_event_emission(self) -> None:
        """Test emissione eventi pygame"""
        dispatcher = event_dispatcher()
        mock_handler = Mock()

        # Registra handler
        dispatcher.register_event(SCENE_ENTER, mock_handler)

        # Emette evento pygame personalizzato
        event = pygame.event.Event(
            SCENE_ENTER, {"scene_name": "test_scene", "data": {"key": "value"}}
        )
        dispatcher.dispatch(event)

        # Verifica che l'handler sia stato chiamato
        mock_handler.assert_called_once_with(event)

    def test_event_priority(self) -> None:
        """Test priorità degli eventi"""
        dispatcher = event_dispatcher()
        mock_handler1 = Mock()
        mock_handler2 = Mock()

        # Registra handler con priorità diverse
        dispatcher.register_event(SCENE_ENTER, mock_handler1, priority=1)
        dispatcher.register_event(SCENE_ENTER, mock_handler2, priority=10)

        # Verifica ordine
        events = dispatcher.get_registered_events()
        handlers = events[SCENE_ENTER]

        assert handlers[0].priority == 10  # Priorità più alta prima
        assert handlers[1].priority == 1

    def test_event_enable_disable(self) -> None:
        """Test abilitazione/disabilitazione eventi"""
        dispatcher = event_dispatcher()
        mock_handler = Mock()

        # Registra handler
        dispatcher.register_event(SCENE_ENTER, mock_handler)

        # Disabilita
        dispatcher.disable_event(SCENE_ENTER, mock_handler)

        # Emette evento
        event = pygame.event.Event(SCENE_ENTER, {"scene_name": "test_scene", "data": {}})
        dispatcher.dispatch(event)

        # Handler non dovrebbe essere chiamato
        mock_handler.assert_not_called()

        # Riabilita
        dispatcher.enable_event(SCENE_ENTER, mock_handler)

        # Emette evento di nuovo
        dispatcher.dispatch(event)

        # Handler dovrebbe essere chiamato
        mock_handler.assert_called_once_with(event)

    def test_event_unregister(self) -> None:
        """Test deregistrazione eventi"""
        dispatcher = event_dispatcher()
        mock_handler = Mock()

        # Registra handler
        dispatcher.register_event(SCENE_ENTER, mock_handler)
        assert len(dispatcher.get_registered_events()[SCENE_ENTER]) == 1

        # Deregistra
        dispatcher.unregister_event(SCENE_ENTER, mock_handler)
        assert len(dispatcher.get_registered_events()[SCENE_ENTER]) == 0

    def test_key_event_registration(self) -> None:
        """Test registrazione eventi tastiera"""
        dispatcher = event_dispatcher()
        mock_handler = Mock()

        # Registra evento tastiera
        dispatcher.register_key_event(pygame.K_SPACE, mock_handler)

        # Emette evento tastiera
        event = pygame.event.Event(pygame.KEYDOWN, key=pygame.K_SPACE)
        dispatcher.dispatch(event)

        # Verifica che l'handler sia stato chiamato
        mock_handler.assert_called_once_with(event)

    def test_key_event_with_condition(self) -> None:
        """Test evento tastiera con condizione aggiuntiva"""
        dispatcher = event_dispatcher()
        mock_handler = Mock()

        def custom_condition(event: pygame.event.Event) -> bool:
            return event.mod & pygame.KMOD_CTRL

        # Registra evento tastiera con condizione
        dispatcher.register_key_event(
            pygame.K_SPACE, mock_handler, condition=custom_condition
        )

        # Emette evento senza CTRL - non dovrebbe chiamare l'handler
        event = pygame.event.Event(pygame.KEYDOWN, key=pygame.K_SPACE)
        dispatcher.dispatch(event)
        mock_handler.assert_not_called()

        # Emette evento con CTRL - dovrebbe chiamare l'handler
        event = pygame.event.Event(
            pygame.KEYDOWN, key=pygame.K_SPACE, mod=pygame.KMOD_CTRL
        )
        dispatcher.dispatch(event)
        mock_handler.assert_called_once_with(event)

    def test_global_conditions(self) -> None:
        """Test condizioni globali"""
        dispatcher = event_dispatcher()
        mock_handler = Mock()

        # Registra condizione globale
        dispatcher.register_global_condition("game_active", lambda: False)
        dispatcher.register_event(SCENE_ENTER, mock_handler)

        # Emette evento - non dovrebbe chiamare l'handler perché la condizione è False
        event = pygame.event.Event(SCENE_ENTER, {"scene_name": "test_scene", "data": {}})
        dispatcher.dispatch(event)
        mock_handler.assert_not_called()

        # Cambia la condizione globale
        dispatcher.register_global_condition("game_active", lambda: True)

        # Emette evento di nuovo - dovrebbe chiamare l'handler
        dispatcher.dispatch(event)
        mock_handler.assert_called_once_with(event)

    def test_error_handling(self) -> None:
        """Test gestione errori negli eventi"""
        dispatcher = event_dispatcher()

        def failing_handler(event: pygame.event.Event) -> None:
            raise ValueError("Test error")

        # Registra handler che fallisce
        dispatcher.register_event(SCENE_ENTER, failing_handler)

        # Emette evento - non dovrebbe sollevare eccezioni
        scene_event = pygame.event.Event(SCENE_ENTER, {"scene_name": "test_scene", "data": {}})
        try:
            dispatcher.dispatch(scene_event)
        except Exception:
            pytest.fail("Il dispatcher dovrebbe gestire gli errori internamente")

    def test_singleton_pattern(self) -> None:
        """Test che il dispatcher sia un singleton"""
        dispatcher1 = event_dispatcher()
        dispatcher2 = event_dispatcher()
        assert dispatcher1 is dispatcher2


class TestSceneEventIntegration:
    """Test per l'integrazione tra Scene e EventDispatcher"""

    def setup_method(self) -> None:
        pygame.init()
        dispatcher = event_dispatcher()
        dispatcher.clear_all_events()

    def teardown_method(self) -> None:
        pygame.quit()

    def _process_pygame_events(self) -> None:
        """Processa tutti gli eventi pygame in coda"""
        for event in pygame.event.get():
            event_dispatcher().dispatch(event)

    def test_scene_emit_scene_event(self) -> None:
        """Test emissione eventi da una scena"""
        scene = Scene[str]("test_scene")
        mock_handler = Mock()

        # Registra handler
        event_dispatcher().register_event(SCENE_CUSTOM, mock_handler)

        # Emette evento dalla scena
        scene.emit_scene_event("custom_event", {"data": "test"})

        # Processa gli eventi pygame
        self._process_pygame_events()

        # Verifica che l'handler sia stato chiamato
        mock_handler.assert_called_once()
        event = mock_handler.call_args[0][0]
        assert event.type == SCENE_CUSTOM
        assert event.scene_name == "test_scene"
        assert event.event_type == "custom_event"
        assert event.data == {"data": "test"}

    def test_scene_lifecycle_events(self) -> None:
        """Test eventi del ciclo di vita delle scene"""
        scene = Scene[str]("test_scene")
        mock_enter = Mock()
        mock_exit = Mock()
        mock_pause = Mock()
        mock_resume = Mock()

        # Registra handler per eventi del ciclo di vita
        event_dispatcher().register_event(SCENE_ENTER, mock_enter)
        event_dispatcher().register_event(SCENE_EXIT, mock_exit)
        event_dispatcher().register_event(SCENE_PAUSE, mock_pause)
        event_dispatcher().register_event(SCENE_RESUME, mock_resume)

        # Testa eventi del ciclo di vita
        scene.on_enter({"level": 1})
        self._process_pygame_events()
        mock_enter.assert_called_once()
        enter_event = mock_enter.call_args[0][0]
        assert enter_event.data == {"level": 1}

        scene.on_pause()
        self._process_pygame_events()
        mock_pause.assert_called_once()

        scene.on_resume()
        self._process_pygame_events()
        mock_resume.assert_called_once()

        scene.on_exit()
        self._process_pygame_events()
        mock_exit.assert_called_once()

    def test_scene_manager_integration(self) -> None:
        """Test integrazione con SceneManager"""
        manager = scene_manager()
        scene = Scene[str]("test_scene")
        mock_handler = Mock()

        # Registra handler per eventi di scena
        event_dispatcher().register_event(SCENE_ENTER, mock_handler)

        # Registra e attiva scena
        manager.register_scene(scene)
        manager.switch_scene("test_scene")

        # Processa gli eventi pygame
        self._process_pygame_events()

        # Verifica che l'evento sia stato emesso
        mock_handler.assert_called_once()
        scene_event = mock_handler.call_args[0][0]
        assert scene_event.scene_name == "test_scene"
        assert scene_event.type == SCENE_ENTER

    def test_custom_scene_events(self) -> None:
        """Test eventi personalizzati di scena"""
        scene = Scene[str]("test_scene")
        mock_handler = Mock()

        # Registra handler per eventi personalizzati
        event_dispatcher().register_event(SCENE_CUSTOM, mock_handler)

        # Emette eventi personalizzati
        scene.emit_scene_event("player_died", {"score": 100})
        scene.emit_scene_event("level_completed", {"level": 5})

        # Processa gli eventi pygame
        self._process_pygame_events()

        # Verifica che gli handler siano stati chiamati
        assert mock_handler.call_count == 2

        # Verifica il primo evento
        first_event = mock_handler.call_args_list[0][0][0]
        assert first_event.event_type == "player_died"
        assert first_event.data == {"score": 100}

        # Verifica il secondo evento
        second_event = mock_handler.call_args_list[1][0][0]
        assert second_event.event_type == "level_completed"
        assert second_event.data == {"level": 5}


if __name__ == "__main__":
    # Inizializza pygame per i test
    pygame.init()

    # Esegui i test
    pytest.main([__file__, "-v"])

    pygame.quit()
