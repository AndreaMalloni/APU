# Event Dispatcher System

Il sistema di Event Dispatcher di APU fornisce un modo avanzato e flessibile per gestire gli eventi del gioco con supporto per condizioni, priorità e azioni specifiche.

## Caratteristiche Principali

- **Singleton Globale**: Un'istanza globale controllata e accessibile da ovunque
- **Condizioni Personalizzate**: Possibilità di specificare condizioni per l'esecuzione degli eventi
- **Sistema di Priorità**: Gli eventi vengono eseguiti in ordine di priorità
- **Condizioni Globali**: Condizioni che si applicano a tutti gli eventi
- **Gestione Errori**: Gestione robusta degli errori durante l'esecuzione
- **Compatibilità**: Mantiene la compatibilità con il codice esistente

## Accesso al Dispatcher

```python
from apu.events import event_dispatcher, EventCondition

# Ottenere l'istanza globale
dispatcher = event_dispatcher()
```

## Registrazione Eventi

### Eventi Semplici

```python
def my_action(event):
    print(f"Evento ricevuto: {event}")

# Registra un evento semplice
dispatcher.register_event(
    event_type=pygame.KEYDOWN,
    action=my_action
)
```

### Eventi con Condizioni

```python
def my_action(event):
    print("Azione eseguita solo se la condizione è soddisfatta")

def my_condition(event):
    return event.key == pygame.K_SPACE

dispatcher.register_event(
    event_type=pygame.KEYDOWN,
    action=my_action,
    condition=my_condition,
    condition_type=EventCondition.CUSTOM
)
```

### Eventi per Tasti Specifici

```python
# Registra un evento per un tasto specifico
dispatcher.register_key_event(
    key=pygame.K_ESCAPE,
    action=quit_game,
    event_type=pygame.KEYDOWN  # opzionale, default è KEYDOWN
)
```

### Eventi con Priorità

```python
# Evento ad alta priorità (eseguito prima)
dispatcher.register_event(
    event_type=pygame.KEYDOWN,
    action=critical_action,
    priority=10
)

# Evento a bassa priorità (eseguito dopo)
dispatcher.register_event(
    event_type=pygame.KEYDOWN,
    action=normal_action,
    priority=1
)
```

## Condizioni Globali

Le condizioni globali si applicano a tutti gli eventi registrati:

```python
def game_active_condition():
    return not game_paused

# Registra una condizione globale
dispatcher.register_global_condition("game_active", game_active_condition)

# Ora tutti gli eventi verranno eseguiti solo se il gioco è attivo
```

## Gestione Eventi

### Abilitare/Disabilitare Eventi

```python
def my_action(event):
    pass

# Disabilita un evento specifico
dispatcher.disable_event(pygame.KEYDOWN, my_action)

# Riabilita un evento
dispatcher.enable_event(pygame.KEYDOWN, my_action)
```

### Rimuovere Eventi

```python
# Rimuove un evento specifico
dispatcher.unregister_event(pygame.KEYDOWN, my_action)

# Rimuove tutti gli eventi
dispatcher.clear_all_events()
```

## Tipi di Condizioni Predefinite

```python
from apu.events import EventCondition

EventCondition.ALWAYS          # Sempre eseguito
EventCondition.KEY_PRESSED     # Solo per pressione tasti
EventCondition.KEY_RELEASED    # Solo per rilascio tasti
EventCondition.MOUSE_IN_AREA   # Solo se il mouse è in un'area
EventCondition.GAME_STATE_ACTIVE  # Solo se il gioco è attivo
EventCondition.CUSTOM          # Condizione personalizzata
```

## Esempio Completo

```python
from apu.events import event_dispatcher, EventCondition
import pygame

class Game:
    def __init__(self):
        self.paused = False
        self.setup_events()
    
    def setup_events(self):
        dispatcher = event_dispatcher()
        
        # Condizione globale
        dispatcher.register_global_condition("not_paused", lambda: not self.paused)
        
        # Eventi di gioco
        dispatcher.register_key_event(
            key=pygame.K_p,
            action=self.toggle_pause
        )
        
        dispatcher.register_key_event(
            key=pygame.K_ESCAPE,
            action=self.quit_game,
            priority=10
        )
        
        # Movimento player (solo se non in pausa)
        dispatcher.register_event(
            event_type=pygame.KEYDOWN,
            action=self.player.move,
            condition=lambda e: e.key in [pygame.K_UP, pygame.K_DOWN, pygame.K_LEFT, pygame.K_RIGHT],
            priority=5
        )
    
    def toggle_pause(self, event):
        self.paused = not self.paused
    
    def quit_game(self, event):
        pygame.quit()
        exit()
    
    def run(self):
        while True:
            for event in pygame.event.get():
                event_dispatcher().dispatch(event)
```

## Best Practices

1. **Usa le Priorità**: Assegna priorità alte agli eventi critici (quit, pause)
2. **Condizioni Globali**: Usa condizioni globali per stati del gioco
3. **Gestione Errori**: Il sistema gestisce automaticamente gli errori
4. **Performance**: Gli eventi disabilitati non vengono processati
5. **Organizzazione**: Raggruppa la registrazione degli eventi in un metodo dedicato

## Compatibilità

Il sistema mantiene la compatibilità con il codice esistente:

```python
# Vecchio modo (ancora funzionante)
from apu.events.dispatcher import __EventDispatcher__
__EventDispatcher__.subscribe(pygame.KEYDOWN, my_action)

# Nuovo modo (raccomandato)
from apu.events import event_dispatcher
event_dispatcher().register_event(pygame.KEYDOWN, my_action)
```
