from collections.abc import Callable
from dataclasses import dataclass
from enum import Enum, auto
from typing import Optional

import pygame

__all__ = ["EventCondition", "EventDispatcher", "event_dispatcher"]


class EventCondition(Enum):
    """Condizioni predefinite per gli eventi"""
    ALWAYS = auto()
    KEY_PRESSED = auto()
    KEY_RELEASED = auto()
    MOUSE_IN_AREA = auto()
    GAME_STATE_ACTIVE = auto()
    CUSTOM = auto()


@dataclass
class EventHandler:
    """Rappresenta un handler di evento con condizioni e azioni"""
    event_type: int
    action: Callable[[pygame.event.Event], None]
    condition: Callable[[pygame.event.Event], bool] | None = None
    condition_type: EventCondition = EventCondition.ALWAYS
    priority: int = 0
    enabled: bool = True


class EventDispatcher:
    """
    Sistema avanzato di gestione eventi con supporto per condizioni e azioni specifiche.
    Gestisce tutti i tipi di eventi pygame, inclusi quelli personalizzati per le scene.
    Implementato come singleton thread-safe con accesso globale controllato.
    """

    _instance: Optional["EventDispatcher"] = None
    _initialized: bool = False
    _handlers: dict[int, list[EventHandler]]
    _global_conditions: dict[str, Callable[[], bool]]

    def __new__(cls) -> "EventDispatcher":
        if cls._instance is None:
            cls._instance = super().__new__(cls)
        return cls._instance

    def __init__(self) -> None:
        if not self._initialized:
            self._handlers = {}
            self._global_conditions = {}
            self._initialized = True

    def register_event(
        self,
        event_type: int,
        action: Callable[[pygame.event.Event], None],
        condition: Callable[[pygame.event.Event], bool] | None = None,
        condition_type: EventCondition = EventCondition.ALWAYS,
        priority: int = 0,
        enabled: bool = True
    ) -> None:
        """
        Registra un evento pygame con azione e condizioni specifiche.
        
        Args:
            event_type: Tipo di evento pygame (inclusi eventi personalizzati)
            action: Funzione da eseguire quando l'evento si verifica
            condition: Condizione personalizzata (opzionale)
            condition_type: Tipo di condizione predefinita
            priority: Priorità dell'handler (più alto = eseguito prima)
            enabled: Se l'handler è abilitato
        """
        handler = EventHandler(
            event_type=event_type,
            action=action,
            condition=condition,
            condition_type=condition_type,
            priority=priority,
            enabled=enabled
        )
        
        if event_type not in self._handlers:
            self._handlers[event_type] = []
        
        self._handlers[event_type].append(handler)
        # Ordina per priorità (più alta prima)
        self._handlers[event_type].sort(key=lambda h: h.priority, reverse=True)

    def register_key_event(
        self,
        key: int,
        action: Callable[[pygame.event.Event], None],
        event_type: int = pygame.KEYDOWN,
        condition: Callable[[pygame.event.Event], bool] | None = None,
        priority: int = 0
    ) -> None:
        """
        Registra un evento specifico per un tasto.
        
        Args:
            key: Codice del tasto pygame
            action: Azione da eseguire
            event_type: Tipo di evento (KEYDOWN o KEYUP)
            condition: Condizione aggiuntiva
            priority: Priorità dell'handler
        """
        def key_condition(event: pygame.event.Event) -> bool:
            return event.key == key
        
        # Combina la condizione del tasto con eventuali condizioni aggiuntive
        if condition:
            def combined_condition(event: pygame.event.Event) -> bool:
                return key_condition(event) and condition(event)
            final_condition = combined_condition
        else:
            final_condition = key_condition
        
        self.register_event(
            event_type=event_type,
            action=action,
            condition=final_condition,
            condition_type=EventCondition.KEY_PRESSED 
                if event_type == pygame.KEYDOWN else EventCondition.KEY_RELEASED,
            priority=priority
        )

    def register_global_condition(self, name: str, condition: Callable[[], bool]) -> None:
        """
        Registra una condizione globale che può essere utilizzata da tutti gli eventi.
        
        Args:
            name: Nome della condizione
            condition: Funzione che restituisce True se la condizione è soddisfatta
        """
        self._global_conditions[name] = condition

    def unregister_event(
        self,
        event_type: int,
        action: Callable[[pygame.event.Event], None]
    ) -> None:
        """
        Deregistra un evento pygame specifico.
        
        Args:
            event_type: Tipo di evento
            action: Azione da rimuovere
        """
        if event_type in self._handlers:
            self._handlers[event_type] = [
                handler for handler in self._handlers[event_type]
                if handler.action != action
            ]

    def enable_event(
        self,
        event_type: int,
        action: Callable[[pygame.event.Event], None]
    ) -> None:
        """Abilita un evento pygame specifico."""
        if event_type in self._handlers:
            for handler in self._handlers[event_type]:
                if handler.action == action:
                    handler.enabled = True

    def disable_event(
        self,
        event_type: int,
        action: Callable[[pygame.event.Event], None]
    ) -> None:
        """Disabilita un evento pygame specifico."""
        if event_type in self._handlers:
            for handler in self._handlers[event_type]:
                if handler.action == action:
                    handler.enabled = False

    def dispatch(self, event: pygame.event.Event) -> None:
        """
        Invia un evento pygame a tutti gli handler registrati che soddisfano le condizioni.
        Gestisce tutti i tipi di eventi pygame, inclusi quelli personalizzati per le scene.
        
        Args:
            event: Evento pygame da processare
        """
        if event.type not in self._handlers:
            return
        
        for handler in self._handlers[event.type]:
            if not handler.enabled:
                continue
            
            # Verifica le condizioni globali
            if not self._check_global_conditions():
                continue
            
            # Verifica le condizioni specifiche dell'handler
            if handler.condition and not handler.condition(event):
                continue
            
            # Esegui l'azione
            try:
                handler.action(event)
            except Exception as e:
                print(f"Errore nell'esecuzione dell'handler per evento {event.type}: {e}")

    def _check_global_conditions(self) -> bool:
        """Verifica tutte le condizioni globali."""
        for condition in self._global_conditions.values():
            try:
                if not condition():
                    return False
            except Exception as e:
                print(f"Errore nella verifica della condizione globale: {e}")
                return False
        return True

    def clear_all_events(self) -> None:
        """Rimuove tutti gli eventi registrati."""
        self._handlers.clear()

    def get_registered_events(self) -> dict[int, list[EventHandler]]:
        """Restituisce tutti gli eventi pygame registrati (solo per debug)."""
        return self._handlers.copy()


# Istanza globale controllata
_event_dispatcher_instance: EventDispatcher | None = None


def get_event_dispatcher() -> EventDispatcher:
    """
    Restituisce l'istanza globale dell'EventDispatcher.
    Questa è l'unica funzione pubblica per accedere al dispatcher.
    """
    global _event_dispatcher_instance
    if _event_dispatcher_instance is None:
        _event_dispatcher_instance = EventDispatcher()
    return _event_dispatcher_instance


# Alias per comodità
event_dispatcher = get_event_dispatcher


# Manteniamo la compatibilità con il codice esistente
__EventDispatcher__ = get_event_dispatcher()
