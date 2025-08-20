# Sistema di Caricamento Mappe

Il framework APU fornisce un sistema modulare e estendibile per il caricamento di mappe da diversi formati, con particolare supporto per i file generati da Tiled Map Editor.

## Panoramica

Il sistema di caricamento è basato su un'architettura a plugin che permette di:
- Caricare mappe da formati diversi (JSON, TMX, formati personalizzati)
- Supportare animazioni dei tile
- Gestire hitbox e collisioni
- Estendere facilmente il supporto per nuovi formati

## Utilizzo Base

### Caricamento Semplice

```python
from apu.loading import load_tiled_map

# Carica una mappa Tiled (JSON o TMX)
sprites = load_tiled_map("path/to/map.json", "path/to/assets/")
```

### Utilizzo Avanzato

```python
from apu.loading import TiledMapLoader, JSONMapLoader, TMXMapLoader

# Crea un loader personalizzato
loader = TiledMapLoader()

# Aggiungi un loader personalizzato
loader.add_loader(MyCustomLoader())

# Carica la mappa
sprites = loader.load("path/to/map.json", "path/to/assets/")
```

## Formati Supportati

### JSON (Tiled)
- **Estensione**: `.json`
- **Descrizione**: Formato JSON esportato da Tiled Map Editor
- **Caratteristiche**: Supporta animazioni, oggetti, layer multipli

### TMX (Tiled)
- **Estensione**: `.tmx`
- **Descrizione**: Formato XML nativo di Tiled Map Editor
- **Caratteristiche**: Supporta compressione, encoding base64, animazioni

## Estendere il Sistema

### Creare un Loader Personalizzato

Per aggiungere il supporto per un nuovo formato di mappa, crea una classe che eredita da `MapLoader`:

```python
from apu.loading import MapLoader
from apu.entities import BaseSprite
from typing import List

class MyCustomLoader(MapLoader):
    def supports_format(self, file_path: str) -> bool:
        return file_path.lower().endswith('.myformat')
    
    def load(self, map_path: str, assets_path: str) -> List[BaseSprite]:
        # Implementa la logica di caricamento per il tuo formato
        sprites = []
        
        # Leggi il file nel formato personalizzato
        with open(map_path, 'r') as f:
            data = f.read()
        
        # Parsing del formato personalizzato
        # ...
        
        # Crea gli sprite
        for tile_data in parsed_data:
            sprite = BaseSprite(
                position=tile_data['position'],
                layer=tile_data['layer'],
                image=tile_data['image']
            )
            sprites.append(sprite)
        
        return sprites
```

### Registrare il Loader

```python
from apu.loading import TiledMapLoader

# Crea il loader principale
loader = TiledMapLoader()

# Aggiungi il tuo loader personalizzato
loader.add_loader(MyCustomLoader())

# Ora il sistema supporta il tuo formato
sprites = loader.load("map.myformat", "assets/")
```

## Struttura delle Classi

### MapLoader (Classe Base Astratta)
- **`load(map_path, assets_path)`**: Carica una mappa e restituisce una lista di sprite
- **`supports_format(file_path)`**: Verifica se il formato è supportato

### TiledMapLoader
- **Loader principale** che delega ai loader specifici
- **`add_loader(loader)`**: Aggiunge un nuovo loader al sistema

### JSONMapLoader
- **Carica mappe JSON** esportate da Tiled
- **Supporta animazioni** e oggetti
- **Gestisce layer multipli**

### TMXMapLoader
- **Carica mappe TMX** (XML) di Tiled
- **Supporta compressione** (gzip, zlib)
- **Supporta encoding** (CSV, base64)

## Caratteristiche Avanzate

### Animazioni dei Tile
Il sistema supporta automaticamente le animazioni dei tile definite in Tiled:

```python
# Le animazioni vengono caricate automaticamente
# e assegnate agli sprite corrispondenti
sprites = load_tiled_map("map.json", "assets/")

# Gli sprite con animazioni avranno già le sequenze configurate
for sprite in sprites:
    if sprite.animations:
        sprite.switch_to("animated")
```

### Hitbox e Collisioni
Le hitbox definite in Tiled vengono caricate automaticamente:

```python
sprites = load_tiled_map("map.json", "assets/")

# Gli sprite con oggetti definiti avranno le hitbox configurate
for sprite in sprites:
    if sprite.solid:
        # Lo sprite ha hitbox configurate
        pass
```

### Layer Multipli
Il sistema rispetta l'ordine dei layer definito in Tiled:

```python
sprites = load_tiled_map("map.json", "assets/")

# Gli sprite sono ordinati per layer
# Layer 0: Background
# Layer 1: Terrain
# Layer 2: Objects
# etc.
```

## Best Practices

### Gestione degli Asset
- Mantieni tutti gli asset in una directory dedicata
- Usa percorsi relativi quando possibile
- Verifica che i tileset siano accessibili

### Performance
- Il caricamento avviene una sola volta all'inizializzazione
- Considera la compressione per mappe grandi
- Usa sprite sheet ottimizzati

### Estendibilità
- Mantieni l'interfaccia `MapLoader` pulita
- Documenta i nuovi formati supportati
- Fornisci esempi di utilizzo

## Esempi Pratici

### Demo Game
Il file `tests/demo/demo.py` mostra un esempio completo di utilizzo:

```python
from apu.loading import load_tiled_map
from apu.scene import TiledScene

# Carica la mappa
map_sprites = load_tiled_map("assets/map.json", "assets/")

# Crea la scena
scene = TiledScene(16, *map_sprites)
```

### Loader Personalizzato Completo
Vedi `CustomMapLoader` in `src/apu/loading.py` per un esempio di implementazione completa.

## Troubleshooting

### Problemi Comuni

1. **File non trovato**: Verifica i percorsi degli asset
2. **Tileset mancante**: Assicurati che il tileset sia nella directory corretta
3. **Formato non supportato**: Verifica l'estensione del file o aggiungi un loader personalizzato

### Debug
Abilita la visualizzazione delle hitbox per verificare il caricamento:

```python
scene = TiledScene(16, *sprites)
scene.show_hitbox = True  # Mostra le hitbox per debug
```
