# Modifiche al Sistema Event Dispatcher

## Panoramica delle Modifiche

Il sistema di Event Dispatcher di APU è stato completamente riscritto per fornire funzionalità avanzate mantenendo la compatibilità con il codice esistente.

## Nuove Funzionalità

### 1. Sistema di Condizioni
- **Condizioni Personalizzate**: Possibilità di specificare funzioni di condizione per ogni evento
- **Condizioni Globali**: Condizioni che si applicano a tutti gli eventi registrati
- **Tipi Predefiniti**: Enum `EventCondition` per condizioni comuni

### 2. Sistema di Priorità
- Gli eventi vengono eseguiti in ordine di priorità (più alta = eseguito prima)
- Utile per eventi critici come quit, pause, etc.

### 3. Istanza Globale Controllata
- Accesso sicuro tramite `event_dispatcher()` o `get_event_dispatcher()`
- Pattern singleton thread-safe
- Non manipolabile a livello di istanza

### 4. Gestione Avanzata Eventi
- Abilitazione/disabilitazione eventi
- Rimozione selettiva di eventi
- Gestione errori robusta

## API Nuova

### Registrazione Eventi

```python
from apu.events import event_dispatcher, EventCondition

dispatcher = event_dispatcher()

# Evento semplice
dispatcher.register_event(
    event_type=pygame.KEYDOWN,
    action=my_function
)

# Evento con condizione
dispatcher.register_event(
    event_type=pygame.KEYDOWN,
    action=my_function,
    condition=lambda e: e.key == pygame.K_SPACE,
    priority=10
)

# Evento per tasto specifico
dispatcher.register_key_event(
    key=pygame.K_ESCAPE,
    action=quit_game
)
```

### Condizioni Globali

```python
# Condizione che si applica a tutti gli eventi
dispatcher.register_global_condition(
    "game_active", 
    lambda: not game_paused
)
```

### Gestione Eventi

```python
# Abilita/disabilita eventi
dispatcher.disable_event(pygame.KEYDOWN, my_function)
dispatcher.enable_event(pygame.KEYDOWN, my_function)

# Rimuovi eventi
dispatcher.unregister_event(pygame.KEYDOWN, my_function)
dispatcher.clear_all_events()
```

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

## Vantaggi del Nuovo Sistema

1. **Flessibilità**: Condizioni personalizzate per ogni evento
2. **Controllo**: Sistema di priorità per eventi critici
3. **Sicurezza**: Istanza globale controllata e non manipolabile
4. **Performance**: Eventi disabilitati non vengono processati
5. **Robustezza**: Gestione errori automatica
6. **Organizzazione**: API più pulita e intuitiva

## Esempi di Utilizzo

### Gestione Stati del Gioco

```python
class Game:
    def __init__(self):
        self.paused = False
        self.setup_events()
    
    def setup_events(self):
        dispatcher = event_dispatcher()
        
        # Condizione globale
        dispatcher.register_global_condition(
            "game_active", 
            lambda: not self.paused
        )
        
        # Eventi che funzionano solo se il gioco è attivo
        dispatcher.register_key_event(
            key=pygame.K_UP,
            action=self.player.move_up
        )
```

### Eventi con Priorità

```python
# Evento critico (alta priorità)
dispatcher.register_key_event(
    key=pygame.K_ESCAPE,
    action=quit_game,
    priority=100
)

# Evento normale (bassa priorità)
dispatcher.register_key_event(
    key=pygame.K_SPACE,
    action=jump,
    priority=10
)
```

### Condizioni Complesse

```python
def complex_condition(event):
    return (
        event.key == pygame.K_SPACE and
        player.has_energy() and
        not player.is_jumping()
    )

dispatcher.register_event(
    event_type=pygame.KEYDOWN,
    action=player.jump,
    condition=complex_condition
)
```

## Migrazione dal Sistema Vecchio

1. **Sostituisci `subscribe` con `register_event`**:
   ```python
   # Vecchio
   __EventDispatcher__.subscribe(pygame.KEYDOWN, my_action)
   
   # Nuovo
   event_dispatcher().register_event(pygame.KEYDOWN, my_action)
   ```

2. **Sostituisci `unsubscribe` con `unregister_event`**:
   ```python
   # Vecchio
   __EventDispatcher__.unsubscribe(pygame.KEYDOWN, my_action)
   
   # Nuovo
   event_dispatcher().unregister_event(pygame.KEYDOWN, my_action)
   ```

3. **Aggiungi condizioni dove necessario**:
   ```python
   # Nuovo: con condizione
   event_dispatcher().register_event(
       pygame.KEYDOWN,
       my_action,
       condition=lambda e: e.key == pygame.K_SPACE
   )
   ```

## File Modificati

- `src/apu/events/dispatcher.py` - Sistema completamente riscritto
- `src/apu/events/__init__.py` - Esportazioni aggiornate
- `src/apu/__init__.py` - Esportazioni principali
- `tests/demo/demo.py` - Esempio aggiornato
- `docs/event_dispatcher.md` - Documentazione completa
- `examples/event_dispatcher_example.py` - Esempio pratico
- `tests/test_new_event_dispatcher.py` - Test del nuovo sistema

## Test

Il nuovo sistema include test completi che verificano:
- Pattern singleton
- Registrazione eventi
- Sistema di priorità
- Condizioni globali
- Abilitazione/disabilitazione
- Gestione errori
- Compatibilità con il sistema vecchio
