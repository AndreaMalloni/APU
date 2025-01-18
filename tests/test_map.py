import unittest
from unittest.mock import MagicMock
from pygame import Surface
from APU.entities import BaseSprite, Drawable
from APU.map import TiledMap  # Adatta l'import al tuo progetto

class TestTiledMap(unittest.TestCase):
    def setUp(self):
        # Mock per Drawable
        self.mock_background = MagicMock(spec=Drawable)
        self.mock_background.draw = MagicMock()

        # Mock per BaseSprite
        self.mock_sprite1 = MagicMock(spec=BaseSprite)
        self.mock_sprite1.layer = 1
        self.mock_sprite1.position = (0, 0)
        self.mock_sprite1.draw = MagicMock()

        self.mock_sprite2 = MagicMock(spec=BaseSprite)
        self.mock_sprite2.layer = 2
        self.mock_sprite2.position = (1, 1)
        self.mock_sprite2.draw = MagicMock()

        # Crea un'istanza di TiledMap
        self.tile_size = (16, 16)
        self.tiled_map = TiledMap(self.tile_size, self.mock_background, self.mock_sprite1, self.mock_sprite2)

    def test_initialization(self):
        # Verifica che la mappa sia inizializzata correttamente
        self.assertEqual(self.tiled_map.tile_size, self.tile_size)
        self.assertIn(1, self.tiled_map.static_items)
        self.assertIn((0, 0), self.tiled_map.static_items[1])
        self.assertEqual(self.tiled_map.static_items[1][(0, 0)], self.mock_sprite1)
        self.assertIn(2, self.tiled_map.static_items)
        self.assertIn((1, 1), self.tiled_map.static_items[2])
        self.assertEqual(self.tiled_map.static_items[2][(1, 1)], self.mock_sprite2)

    def test_insert(self):
        # Mock per un nuovo sprite
        mock_sprite3 = MagicMock(spec=BaseSprite)
        mock_sprite3.layer = 1
        mock_sprite3.position = (2, 2)
        mock_sprite3.draw = MagicMock()

        # Inserisci il nuovo sprite
        self.tiled_map.insert(mock_sprite3)

        # Verifica che lo sprite sia stato aggiunto correttamente
        self.assertIn(1, self.tiled_map.static_items)
        self.assertIn((2, 2), self.tiled_map.static_items[1])
        self.assertEqual(self.tiled_map.static_items[1][(2, 2)], mock_sprite3)

    def test_render(self):
        # Mock per una superficie di destinazione
        mock_surface = MagicMock(spec=Surface)

        # Chiama il metodo render
        self.tiled_map.render(mock_surface)

        # Verifica che il background sia stato disegnato
        self.mock_background.draw.assert_called_once_with(mock_surface)

        # Verifica che tutti gli sprite siano stati disegnati
        self.mock_sprite1.draw.assert_called_once_with(mock_surface)
        self.mock_sprite2.draw.assert_called_once_with(mock_surface)

    def test_empty_map(self):
        # Crea una nuova mappa senza sprite
        empty_map = TiledMap(self.tile_size, self.mock_background)

        # Verifica che la mappa sia inizialmente vuota
        self.assertEqual(empty_map.static_items, {})

        # Mock per una superficie di destinazione
        mock_surface = MagicMock(spec=Surface)

        # Chiama il metodo render
        empty_map.render(mock_surface)

        # Verifica che solo il background sia stato disegnato
        self.mock_background.draw.assert_called_once_with(mock_surface)

    def test_overwrite_sprite(self):
        # Mock per uno sprite nella stessa posizione e layer
        mock_sprite_new = MagicMock(spec=BaseSprite)
        mock_sprite_new.layer = 1
        mock_sprite_new.position = (0, 0)
        mock_sprite_new.draw = MagicMock()

        # Inserisci il nuovo sprite nella stessa posizione del primo
        self.tiled_map.insert(mock_sprite_new)

        # Verifica che lo sprite precedente sia stato sovrascritto
        self.assertEqual(self.tiled_map.static_items[1][(0, 0)], mock_sprite_new)

if __name__ == '__main__':
    unittest.main()
