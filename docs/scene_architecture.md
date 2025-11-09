# Architettura Scene di APU con Eventi Pygame Personalizzati

L'architettura di Scene di APU fornisce un sistema flessibile e generico per gestire contenuti di gioco, con supporto per gerarchie, layer di rendering e **eventi pygame personalizzati** per una gestione completamente unificata.

## Caratteristiche Principali

- **Gerarchia di Scene**: Sistema di scene annidate e organizzate
- **SceneManager Globale**: Gestione centralizzata delle scene con stack
- **Layer di Rendering**: Sistema di layer predefiniti e personalizzabili
- **Eventi Pygame Personalizzati**: Sistema unificato di eventi per scene e pygame
- **Camera e Transizioni**: Supporto per camera e transizioni tra scene
- **Compatibilità**: Mantiene la compatibilità con il codice esistente

## Eventi Pygame Personalizzati per le Scene

### Problema Risolto: Ridondanza di Responsabilità

Prima dell'integrazione, avevamo due sistemi di eventi separati:
1. **Event Dispatcher**: Gestiva eventi pygame (KEYDOWN, MOUSEBUTTONDOWN, etc.)
2. **Eventi di Scena**: Gestiva eventi interni delle scene (scene_enter, scene_exit, etc.)

### Soluzione: Eventi Pygame Personalizzati

Ora tutti gli eventi sono **eventi pygame personalizzati** gestiti dallo stesso sistema:

```python
from apu.scene import SCENE_ENTER, SCENE_EXIT, SCENE_CUSTOM
from apu.events import event_dispatcher

# Eventi pygame standard
event_dispatcher().register_key_event(pygame.K_SPACE, jump_action)

# Eventi pygame personalizzati per le scene
event_dispatcher().register_event(SCENE_ENTER, on_scene_enter)
event_dispatcher().register_event(SCENE_EXIT, on_scene_exit)
```

## Tipi di Eventi Personalizzati

```python
from apu.scene import (
    SCENE_ENTER,    # pygame.USEREVENT + 1
    SCENE_EXIT,     # pygame.USEREVENT + 2
    SCENE_PAUSE,    # pygame.USEREVENT + 3
    SCENE_RESUME,   # pygame.USEREVENT + 4
    SCENE_CUSTOM    # pygame.USEREVENT + 5
)
```

## Componenti Principali

### SceneNode
Classe base per tutti i nodi della gerarchia di scene.

```python
from apu.scene import SceneNode

class MyNode(SceneNode):
    def __init__(self, name: str):
        super().__init__(name)
        
    def update(self, dt: float):
        # Logica di aggiornamento
        pass
        
    def render(self, surface: pygame.Surface, camera=None):
        # Logica di rendering
        pass
```

### Scene
Classe base per tutte le scene, estende SceneNode.

```python
from apu.scene import Scene, RenderLayer

class MyScene(Scene[MyItemType]):
    def __init__(self, name: str):
        super().__init__(name)
        
    def add_item(self, item: MyItemType, layer: RenderLayer = RenderLayer.ENTITIES):
        # Aggiunge un elemento alla scena
        pass
```

### SceneManager
Gestore globale delle scene con stack e transizioni.

```python
from apu.scene import scene_manager

# Registra una scena
scene_manager().register_scene(my_scene)

# Cambia scena
scene_manager().switch_scene("scene_name")

# Aggiungi scena allo stack
scene_manager().push_scene("scene_name")

# Rimuovi scena dallo stack
scene_manager().pop_scene()
```

## Gestione Eventi Unificata

### Eventi Pygame Standard
```python
from apu.events import event_dispatcher

# Evento semplice
event_dispatcher().register_event(pygame.KEYDOWN, my_action)

# Evento con condizione
event_dispatcher().register_event(
    pygame.KEYDOWN, 
    my_action,
    condition=lambda e: e.key == pygame.K_SPACE
)

# Evento per tasto specifico
event_dispatcher().register_key_event(pygame.K_ESCAPE, quit_action)
```

### Eventi Pygame Personalizzati per Scene
```python
from apu.scene import SCENE_ENTER, SCENE_EXIT, SCENE_CUSTOM
from apu.events import event_dispatcher

# Handler per eventi di scena
def on_scene_enter(event):
    scene_name = event.scene_name
    data = event.data
    print(f"Scena '{scene_name}' entrata con dati: {data}")

def on_scene_exit(event):
    scene_name = event.scene_name
    print(f"Scena '{scene_name}' uscita")

# Registra handler
event_dispatcher().register_event(SCENE_ENTER, on_scene_enter)
event_dispatcher().register_event(SCENE_EXIT, on_scene_exit)
```

### Eventi Personalizzati di Scena
```python
class MyScene(Scene):
    def __init__(self, name: str):
        super().__init__(name)
        
    def custom_action(self):
        # Emette evento personalizzato come evento pygame
        self.emit_scene_event("player_died", {"score": 100, "level": 5})

# Handler per evento personalizzato
def on_scene_custom_event(event):
    if event.event_type == "player_died":
        print(f"Player morto nella scena {event.scene_name}")
        print(f"Score: {event.data['score']}")

event_dispatcher().register_event(SCENE_CUSTOM, on_scene_custom_event)
```

## Layer di Rendering

Il sistema fornisce layer predefiniti per organizzare il rendering:

```python
from apu.scene import RenderLayer

RenderLayer.BACKGROUND   # Sfondo
RenderLayer.TERRAIN      # Terreno
RenderLayer.DECORATIONS  # Decorazioni
RenderLayer.ENTITIES     # Entità
RenderLayer.UI           # Interfaccia utente
RenderLayer.OVERLAY      # Overlay
```

### Layer Personalizzati

Puoi creare layer personalizzati usando stringhe:

```python
# Aggiungi elemento a layer personalizzato
scene.add_item(item, "particles")
scene.add_item(item, "effects")
scene.add_item(item, "debug")
```

## Stati delle Scene

Le scene possono avere diversi stati:

```python
from apu.scene import SceneState

SceneState.INACTIVE      # Inattiva
SceneState.LOADING       # Caricamento
SceneState.ACTIVE        # Attiva
SceneState.PAUSED        # In pausa
SceneState.TRANSITIONING # In transizione
SceneState.UNLOADING     # Scaricamento
```

## Camera

Sistema di camera integrato per il rendering:

```python
from apu.scene import Camera

# Crea camera
camera = Camera(position=(0, 0), zoom=1.0)

# Segui un target
camera.follow(player_position, dt)

# Converti coordinate
screen_pos = camera.world_to_screen(world_pos)
world_pos = camera.screen_to_world(screen_pos)
```

## Esempi di Utilizzo

### Scena Semplice con Eventi Unificati

```python
from apu.scene import Scene, RenderLayer, SCENE_ENTER
from apu.events import event_dispatcher

class GameScene(Scene[pygame.Rect]):
    def __init__(self):
        super().__init__("game")
        
    def add_game_object(self, rect: pygame.Rect):
        self.add_item(rect, RenderLayer.ENTITIES)
        
    def render(self, surface: pygame.Surface, camera=None):
        # Rendi tutti gli elementi
        for layer in RenderLayer:
            items = self.get_items(layer)
            for item in items:
                pygame.draw.rect(surface, (255, 255, 255), item)

# Setup eventi
def on_game_start(event):
    print("Game started")

event_dispatcher().register_event(SCENE_ENTER, on_game_start)
event_dispatcher().register_key_event(pygame.K_SPACE, lambda e: print("Jump!"))
```

### Scena con UI e Eventi

```python
class MenuScene(Scene[str]):
    def __init__(self):
        super().__init__("menu")
        self.options = ["Play", "Settings", "Quit"]
        
    def render(self, surface: pygame.Surface, camera=None):
        surface.fill((50, 50, 100))
        
        for i, option in enumerate(self.options):
            # Rendi opzioni del menu
            pass

# Eventi per menu
def on_menu_open(event):
    print("Menu opened")

event_dispatcher().register_event(SCENE_ENTER, on_menu_open)
event_dispatcher().register_key_event(pygame.K_UP, lambda e: print("Navigate up"))
event_dispatcher().register_key_event(pygame.K_DOWN, lambda e: print("Navigate down"))
```

### Gerarchia di Scene

```python
# Crea scene
main_menu = MenuScene()
game_scene = GameScene()
pause_menu = PauseScene()

# Aggiungi figli
main_menu.add_child(game_scene)
game_scene.add_child(pause_menu)

# Aggiorna gerarchia
main_menu.update_hierarchy(dt)
main_menu.render_hierarchy(surface)
```

### SceneManager con Stack

```python
# Setup
manager = scene_manager()
manager.register_scene(main_menu)
manager.register_scene(game_scene)
manager.register_scene(pause_menu)

# Navigazione
manager.switch_scene("menu")           # Menu principale
manager.push_scene("game")             # Aggiungi gioco
manager.push_scene("pause")            # Aggiungi pausa
manager.pop_scene()                    # Torna al gioco
manager.pop_scene()                    # Torna al menu
```

## TiledScene (Compatibilità)

La classe `TiledScene` mantiene la compatibilità con il codice esistente:

```python
from apu.scene import TiledScene

# Vecchio modo (ancora funzionante)
tiled_scene = TiledScene("level1", 16)
tiled_scene.insert(sprite1, sprite2, sprite3)

# Nuovo modo
tiled_scene = TiledScene("level1", 16)
tiled_scene.insert(sprite1, sprite2, sprite3)
tiled_scene.add_item(sprite4, RenderLayer.ENTITIES)
```

## Best Practices

### 1. Organizzazione delle Scene

```python
# Struttura consigliata
class Game:
    def __init__(self):
        self.scene_manager = scene_manager()
        self.setup_scenes()
        self.setup_events()
        
    def setup_scenes(self):
        # Crea e registra scene
        self.menu_scene = MenuScene()
        self.game_scene = GameScene()
        self.scene_manager.register_scene(self.menu_scene)
        self.scene_manager.register_scene(self.game_scene)
        
    def setup_events(self):
        # Eventi pygame standard
        event_dispatcher().register_key_event(pygame.K_ESCAPE, self.quit_game)
        
        # Eventi pygame personalizzati per scene
        event_dispatcher().register_event(SCENE_ENTER, self.on_scene_enter)
```

### 2. Gestione degli Eventi Unificati

```python
class MyScene(Scene):
    def __init__(self, name: str):
        super().__init__(name)
        self.setup_events()
        
    def setup_events(self):
        # Handler per aggiornamento
        self.add_update_handler(self.custom_update)
        
        # Handler per rendering
        self.add_render_handler(self.custom_render)
        
    def custom_action(self):
        # Emette evento personalizzato come evento pygame
        self.emit_scene_event("custom_event", {"data": "value"})
```

### 3. Layer di Rendering

```python
# Usa layer appropriati
scene.add_item(background, RenderLayer.BACKGROUND)
scene.add_item(terrain, RenderLayer.TERRAIN)
scene.add_item(player, RenderLayer.ENTITIES)
scene.add_item(ui, RenderLayer.UI)
scene.add_item(particles, "particles")  # Layer personalizzato
```

### 4. Transizioni

```python
# Transizioni con dati
scene_manager().push_scene("game", {
    "level": 1,
    "player_health": 100,
    "score": 0
})

# Gestisci dati nella scena tramite eventi
def on_scene_enter(event):
    if event.scene_name == "game":
        level = event.data.get("level", 1)
        health = event.data.get("player_health", 100)

event_dispatcher().register_event(SCENE_ENTER, on_scene_enter)
```

## Vantaggi degli Eventi Pygame Personalizzati

1. **Sistema Completamente Unificato**: Un solo sistema di eventi per tutto
2. **Semplicità**: Nessuna API separata da imparare
3. **Performance**: Gestione centralizzata degli eventi
4. **Debugging**: Più facile tracciare e debuggare eventi
5. **Estendibilità**: Facile aggiungere nuovi tipi di eventi
6. **Compatibilità**: Funziona con tutti i sistemi pygame esistenti

## Migrazione dal Sistema Vecchio

### 1. Eventi di Scena

```python
# Vecchio modo (non più disponibile)
scene.add_event_handler("scene_enter", handler)
scene.emit_event("custom_event", data)

# Nuovo modo
event_dispatcher().register_event(SCENE_ENTER, handler)
scene.emit_scene_event("custom_event", data)
```

### 2. TiledScene

```python
# Vecchio
tiled_scene = TiledScene(16, *sprites)

# Nuovo
tiled_scene = TiledScene("level_name", 16)
tiled_scene.insert(*sprites)
```

### 3. Rendering

```python
# Vecchio
tiled_scene.render(surface)

# Nuovo
scene_manager().render(surface)
```

### 4. Aggiornamento

```python
# Vecchio
tiled_scene.update()

# Nuovo
scene_manager().update(dt)
```

## Esempi Avanzati

### Scena con Particelle e Eventi

```python
class ParticleScene(Scene[Particle]):
    def __init__(self):
        super().__init__("particles")
        self.add_render_handler(self.render_particles)
        
    def render_particles(self, surface, camera):
        for particle in self.get_items("particles"):
            particle.render(surface, camera)
            
    def create_explosion(self, position):
        # Crea particelle
        for i in range(10):
            particle = Particle(position)
            self.add_item(particle, "particles")
        
        # Emette evento personalizzato
        self.emit_scene_event("explosion_created", {"position": position})

# Handler per esplosione
def on_explosion(event):
    if event.event_type == "explosion_created":
        print(f"Esplosione in {event.data['position']}")

event_dispatcher().register_event(SCENE_CUSTOM, on_explosion)
```

### Scena con Fisica

```python
class PhysicsScene(Scene[PhysicsObject]):
    def __init__(self):
        super().__init__("physics")
        self.add_update_handler(self.update_physics)
        
    def update_physics(self, dt):
        for obj in self.get_items(RenderLayer.ENTITIES):
            obj.update_physics(dt)
            
    def collision_detected(self, obj1, obj2):
        self.emit_scene_event("collision", {
            "object1": obj1,
            "object2": obj2
        })

# Handler per collisioni
def on_collision(event):
    if event.event_type == "collision":
        print(f"Collisione tra {event.data['object1']} e {event.data['object2']}")

event_dispatcher().register_event(SCENE_CUSTOM, on_collision)
```

### Scena Multiplayer

```python
class MultiplayerScene(Scene[Player]):
    def __init__(self):
        super().__init__("multiplayer")
        
    def player_joined(self, player_data):
        player = Player(player_data)
        self.add_item(player, RenderLayer.ENTITIES)
        
        # Emette evento
        self.emit_scene_event("player_joined", player_data)
        
    def player_left(self, player_id):
        # Rimuovi player
        for player in self.find_items(lambda p: p.id == player_id):
            self.remove_item(player)
            
        # Emette evento
        self.emit_scene_event("player_left", {"player_id": player_id})

# Handler per eventi multiplayer
def on_multiplayer_event(event):
    if event.event_type == "player_joined":
        print(f"Player {event.data['name']} joined")
    elif event.event_type == "player_left":
        print(f"Player {event.data['player_id']} left")

event_dispatcher().register_event(SCENE_CUSTOM, on_multiplayer_event)
```
