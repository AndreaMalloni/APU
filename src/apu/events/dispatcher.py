from collections.abc import Callable

import pygame

__all__ = ["__EventDispatcher__"]


class EventDispatcher:
    """
    Soggetto centrale che gestisce e distribuisce gli eventi Pygame
    utilizzando un sistema di dispatcher.
    Questa classe è ora implementata come un robusto singleton.
    """

    _instance = None
    _listeners: dict[int, list[Callable[[pygame.event.Event], None]]]

    def __new__(cls) -> "EventDispatcher":
        if cls._instance is None:
            cls._instance = super().__new__(cls)
            cls._instance._listeners = {}
        return cls._instance

    def subscribe(self, event_type: int, listener: Callable[[pygame.event.Event], None]) -> None:
        """
        Registra un listener per un tipo di evento specifico.
        """
        if event_type not in self._listeners:
            self._listeners[event_type] = []
        if listener not in self._listeners[event_type]:
            self._listeners[event_type].append(listener)

    def unsubscribe(self, event_type: int, listener: Callable[[pygame.event.Event], None]) -> None:
        """
        Deregistra un listener da un tipo di evento specifico.
        """
        if event_type in self._listeners and listener in self._listeners[event_type]:
            self._listeners[event_type].remove(listener)

    def dispatch(self, event: pygame.event.Event) -> None:
        """
        Invia un evento a tutti i listener registrati per il suo tipo.
        """
        if event.type in self._listeners:
            for listener in self._listeners[event.type]:
                listener(event)


__EventDispatcher__: EventDispatcher = EventDispatcher()
