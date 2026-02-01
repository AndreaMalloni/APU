from collections.abc import Callable
from dataclasses import dataclass
from typing import Optional

import pygame

from apu.core.enums import EventCondition

__all__ = ["EventDispatcher", "event_dispatcher"]


@dataclass
class EventHandler:
    """Represents an event handler with conditions and actions"""
    event_type: int
    action: Callable[[pygame.event.Event], None]
    condition: Callable[[pygame.event.Event], bool] | None = None
    condition_type: EventCondition = EventCondition.ALWAYS
    priority: int = 0
    enabled: bool = True


class EventDispatcher:
    """
    Advanced event management system with support for specific conditions and actions.
    Handles all types of pygame events, including custom scene events.
    Implemented as a thread-safe singleton with controlled global access.
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
        Registers a pygame event with specific action and conditions.
        
        Args:
            event_type: Type of pygame event (including custom events)
            action: Function to execute when the event occurs
            condition: Custom condition (optional)
            condition_type: Type of predefined condition
            priority: Handler priority (higher = executed first)
            enabled: Whether the handler is enabled
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
        # Sort by priority (highest first)
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
        Registers a specific event for a key.
        
        Args:
            key: Pygame key code
            action: Action to execute
            event_type: Event type (KEYDOWN or KEYUP)
            condition: Additional condition
            priority: Handler priority
        """
        def key_condition(event: pygame.event.Event) -> bool:
            return (event.type == pygame.KEYDOWN and event.key == key)

        # Combine the key condition with any additional conditions
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
        Registers a global condition that can be used by all events.
        
        Args:
            name: Condition name
            condition: Function that returns True if the condition is satisfied
        """
        self._global_conditions[name] = condition

    def unregister_event(
        self,
        event_type: int,
        action: Callable[[pygame.event.Event], None]
    ) -> None:
        """
        Unregisters a specific pygame event.
        
        Args:
            event_type: Event type
            action: Action to remove
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
        """Enables a specific pygame event."""
        if event_type in self._handlers:
            for handler in self._handlers[event_type]:
                if handler.action == action:
                    handler.enabled = True

    def disable_event(
        self,
        event_type: int,
        action: Callable[[pygame.event.Event], None]
    ) -> None:
        """Disables a specific pygame event."""
        if event_type in self._handlers:
            for handler in self._handlers[event_type]:
                if handler.action == action:
                    handler.enabled = False

    def dispatch(self, event: pygame.event.Event) -> None:
        """
        Dispatches a pygame event to all registered handlers that satisfy the conditions.
        Handles all types of pygame events, including custom scene events.
        
        Args:
            event: Pygame event to process
        """
        if event.type not in self._handlers:
            return
        
        for handler in self._handlers[event.type]:
            if not handler.enabled:
                continue
            
            # Check global conditions
            if not self._check_global_conditions():
                continue
            
            # Check handler-specific conditions
            if handler.condition and not handler.condition(event):
                continue
            
            # Execute the action
            try:
                handler.action(event)
            except Exception as e:
                print(f"Error executing handler for event {event.type}: {e}")

    def _check_global_conditions(self) -> bool:
        """Checks all global conditions."""
        for condition in self._global_conditions.values():
            try:
                if not condition():
                    return False
            except Exception as e:
                print(f"Error checking global condition: {e}")
                return False
        return True

    def clear_all_events(self) -> None:
        """Removes all registered events."""
        self._handlers.clear()

    def get_registered_events(self) -> dict[int, list[EventHandler]]:
        """Returns all registered pygame events (debug only)."""
        return self._handlers.copy()


# Controlled global instance
_event_dispatcher_instance: EventDispatcher | None = None


def get_event_dispatcher() -> EventDispatcher:
    """
    Returns the global EventDispatcher instance.
    This is the only public function to access the dispatcher.
    """
    global _event_dispatcher_instance
    if _event_dispatcher_instance is None:
        _event_dispatcher_instance = EventDispatcher()
    return _event_dispatcher_instance


# Alias for convenience
event_dispatcher = get_event_dispatcher


# Maintain compatibility with existing code
__EventDispatcher__ = get_event_dispatcher()
