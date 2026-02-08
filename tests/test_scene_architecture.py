from unittest.mock import Mock

import pygame
import pytest
from typing_extensions import override

from apu.camera import Camera
from apu.core.enums import RenderLayer
from apu.scene import Scene, SceneManager, SceneNode, SceneState, scene_manager


class TestSceneNode:
    """Test per la classe base SceneNode"""

    def setup_method(self) -> None:
        pygame.init()

    def teardown_method(self) -> None:
        pygame.quit()

    def test_scene_node_creation(self) -> None:
        """Test creazione di un nodo scena"""

        # Creiamo una classe concreta per testare SceneNode
        class ConcreteSceneNode(SceneNode):
            @override
            def update(self, dt: float) -> None:
                pass

            @override
            def render(self, surface: pygame.Surface, camera: Camera | None = None) -> None:
                pass

        node = ConcreteSceneNode("test_node")
        assert node.name == "test_node"
        assert node.state == SceneState.INACTIVE
        assert node.visible is True
        assert node.enabled is True

    def test_scene_node_hierarchy(self) -> None:
        """Test gerarchia di nodi"""

        class ConcreteSceneNode(SceneNode):
            @override
            def update(self, dt: float) -> None:
                pass

            @override
            def render(self, surface: pygame.Surface, camera: Camera | None = None) -> None:
                pass

        parent = ConcreteSceneNode("parent")
        child1 = ConcreteSceneNode("child1")
        child2 = ConcreteSceneNode("child2")

        parent.add_child(child1)
        parent.add_child(child2)

        assert len(parent.children) == 2
        assert child1.parent == parent
        assert child2.parent == parent

    def test_scene_node_find(self) -> None:
        """Test ricerca di nodi nella gerarchia"""

        class ConcreteSceneNode(SceneNode):
            @override
            def update(self, dt: float) -> None:
                pass

            @override
            def render(self, surface: pygame.Surface, camera: Camera | None = None) -> None:
                pass

        root = ConcreteSceneNode("root")
        child1 = ConcreteSceneNode("child1")
        child2 = ConcreteSceneNode("child2")
        grandchild = ConcreteSceneNode("grandchild")

        root.add_child(child1)
        root.add_child(child2)
        child1.add_child(grandchild)

        found = root.find_child("grandchild")
        assert found == grandchild

        not_found = root.find_child("nonexistent")
        assert not_found is None


class TestScene:
    """Test per la classe base Scene"""

    def setup_method(self) -> None:
        pygame.init()

    def teardown_method(self) -> None:
        pygame.quit()

    def test_scene_creation(self) -> None:
        """Test creazione di una scena"""
        scene = Scene[str]("test_scene")
        assert scene.name == "test_scene"
        assert isinstance(scene.camera, Camera)

    def test_scene_add_remove_items(self) -> None:
        """Test aggiunta e rimozione di elementi"""
        scene = Scene[str]("test_scene")
        item1 = "item1"
        item2 = "item2"

        scene.add_item(item1, RenderLayer.ENTITIES)
        scene.add_item(item2, RenderLayer.BACKGROUND)

        entities = scene.get_items(RenderLayer.ENTITIES)
        background = scene.get_items(RenderLayer.BACKGROUND)

        assert len(entities) == 1
        assert len(background) == 1
        assert item1 in entities
        assert item2 in background

        scene.remove_item(item1)
        entities = scene.get_items(RenderLayer.ENTITIES)
        assert len(entities) == 0

    def test_scene_custom_layers(self) -> None:
        """Test layer personalizzati"""
        scene = Scene[str]("test_scene")
        item1 = "item1"
        item2 = "item2"

        scene.add_item(item1, "custom_layer")
        scene.add_item(item2, "another_layer")

        custom_items = scene.get_items("custom_layer")
        another_items = scene.get_items("another_layer")

        assert len(custom_items) == 1
        assert len(another_items) == 1
        assert item1 in custom_items
        assert item2 in another_items

    def test_scene_state_transitions(self) -> None:
        """Test transizioni di stato"""
        scene = Scene[str]("test_scene")

        assert scene.state == SceneState.INACTIVE

        scene.on_enter({"level": 1})
        assert scene.state == SceneState.ACTIVE  # type: ignore[comparison-overlap]

        scene.on_pause()
        assert scene.state == SceneState.PAUSED

        scene.on_resume()
        assert scene.state == SceneState.ACTIVE

        scene.on_exit()
        assert scene.state == SceneState.INACTIVE

    def test_scene_update_handlers(self) -> None:
        """Test handler di aggiornamento"""
        scene = Scene[str]("test_scene")
        mock_handler = Mock()

        scene.add_update_handler(mock_handler)
        # Imposta la scena come attiva per permettere l'aggiornamento
        scene.state = SceneState.ACTIVE
        scene.update(0.016)  # Simula 60 FPS

        mock_handler.assert_called_once_with(0.016)

    def test_scene_render_handlers(self) -> None:
        """Test handler di rendering"""
        scene = Scene[str]("test_scene")
        mock_handler = Mock()
        surface = pygame.Surface((800, 600))

        scene.add_render_handler(mock_handler)
        scene.render(surface)

        mock_handler.assert_called_once_with(surface, scene.camera)

    def test_scene_find_items(self) -> None:
        """Test ricerca elementi con predicato"""
        scene = Scene[str]("test_scene")
        scene.add_item("player", RenderLayer.ENTITIES)
        scene.add_item("enemy", RenderLayer.ENTITIES)
        scene.add_item("background", RenderLayer.BACKGROUND)

        # Trova elementi che iniziano con 'p'
        player_items = list(scene.find_items(lambda item: item.startswith("p")))
        assert len(player_items) == 1
        assert "player" in player_items

    def test_scene_iteration(self) -> None:
        """Test iterazione sulla scena"""
        scene = Scene[str]("test_scene")
        scene.add_item("item1", RenderLayer.ENTITIES)
        scene.add_item("item2", RenderLayer.BACKGROUND)

        items = list(scene)
        assert len(items) == 2
        assert "item1" in items
        assert "item2" in items


class TestSceneManager:
    """Test per il SceneManager"""

    def setup_method(self) -> None:
        pygame.init()

    def teardown_method(self) -> None:
        pygame.quit()

    def test_scene_manager_singleton(self) -> None:
        """Test che il SceneManager sia un singleton"""
        manager1 = scene_manager()
        manager2 = scene_manager()
        assert manager1 is manager2

    def test_scene_registration(self) -> None:
        """Test registrazione scene"""
        manager = scene_manager()
        scene = Scene[str]("test_scene")

        manager.register_scene(scene)
        assert "test_scene" in manager._scenes

    def test_scene_switching(self) -> None:
        """Test cambio di scena"""
        manager = scene_manager()
        scene1 = Scene[str]("scene1")
        scene2 = Scene[str]("scene2")

        manager.register_scene(scene1)
        manager.register_scene(scene2)

        manager.switch_scene("scene1")
        assert manager.get_active_scene() == scene1
        assert scene1.state == SceneState.ACTIVE

        manager.switch_scene("scene2")
        assert manager.get_active_scene() == scene2
        assert scene1.state == SceneState.INACTIVE  # type: ignore[comparison-overlap]
        assert scene2.state == SceneState.ACTIVE

    def test_scene_stack(self) -> None:
        """Test stack di scene"""
        manager = SceneManager()  # Create a fresh instance for the stack test
        scene1 = Scene[str]("scene1")
        scene2 = Scene[str]("scene2")

        manager.register_scene(scene1)
        manager.register_scene(scene2)

        # Push scene
        manager.push_scene("scene1")
        assert manager.get_active_scene() == scene1
        assert len(manager._scene_stack) == 0

        manager.push_scene("scene2")
        assert manager.get_active_scene() == scene2
        assert len(manager._scene_stack) == 1
        assert scene1.state == SceneState.PAUSED

        # Pop scene
        popped = manager.pop_scene()
        assert popped == scene1
        assert manager.get_active_scene() == scene1
        assert scene1.state == SceneState.ACTIVE  # type: ignore[comparison-overlap]
        assert len(manager._scene_stack) == 0

    def test_scene_unregister(self) -> None:
        """Test deregistrazione scene"""
        manager = scene_manager()
        scene = Scene[str]("test_scene")

        manager.register_scene(scene)
        assert "test_scene" in manager._scenes

        manager.unregister_scene("test_scene")
        assert "test_scene" not in manager._scenes

    def test_scene_manager_update_render(self) -> None:
        """Test aggiornamento e rendering del manager"""
        manager = scene_manager()
        scene = Scene[str]("test_scene")
        mock_update_handler = Mock()
        mock_render_handler = Mock()

        scene.add_update_handler(mock_update_handler)
        scene.add_render_handler(mock_render_handler)

        manager.register_scene(scene)
        manager.switch_scene("test_scene")

        # Test update
        manager.update(0.016)
        mock_update_handler.assert_called_once_with(0.016)

        # Test render
        surface = pygame.Surface((800, 600))
        manager.render(surface)
        mock_render_handler.assert_called_once_with(surface, scene.camera)


class TestCamera:
    """Test per la classe Camera"""

    def setup_method(self) -> None:
        pygame.init()

    def teardown_method(self) -> None:
        pygame.quit()

    def test_camera_creation(self) -> None:
        """Test creazione camera"""
        camera = Camera(position=(100, 200), zoom=2.0)
        assert camera.position == [100, 200]
        assert camera.zoom == 2.0

    def test_camera_coordinate_conversion(self) -> None:
        """Test conversione coordinate"""
        camera = Camera(position=(100, 100), zoom=1.0)

        # World to screen
        screen_pos = camera.world_to_screen((150, 150))
        assert screen_pos == (50, 50)

        # Screen to world
        world_pos = camera.screen_to_world((50, 50))
        assert world_pos == (150, 150)

    def test_camera_follow(self) -> None:
        """Test follow della camera"""
        camera = Camera(position=(0, 0), zoom=1.0)

        camera.follow((100, 100), 1.0)
        assert camera.target_position == [100, 100]

    def test_camera_zoom_effects(self) -> None:
        """Test effetti dello zoom"""
        camera = Camera(position=(0, 0), zoom=2.0)

        # World to screen con zoom
        screen_pos = camera.world_to_screen((100, 100))
        assert screen_pos == (200, 200)

        # Screen to world con zoom
        world_pos = camera.screen_to_world((200, 200))
        assert world_pos == (100, 100)


class TestRenderLayer:
    """Test per i layer di rendering"""

    def test_render_layer_enum(self) -> None:
        """Test enum RenderLayer"""
        assert RenderLayer.BACKGROUND
        assert RenderLayer.TERRAIN
        assert RenderLayer.DECORATIONS
        assert RenderLayer.ENTITIES
        assert RenderLayer.UI
        assert RenderLayer.OVERLAY

    def test_render_layer_ordering(self) -> None:
        """Test ordine dei layer"""
        layers = list(RenderLayer)
        # Verifica che BACKGROUND sia prima di OVERLAY
        assert layers.index(RenderLayer.BACKGROUND) < layers.index(RenderLayer.OVERLAY)


class TestSceneState:
    """Test per gli stati delle scene"""

    def setup_method(self) -> None:
        pygame.init()

    def teardown_method(self) -> None:
        pygame.quit()

    def test_scene_state_enum(self) -> None:
        """Test enum SceneState"""
        assert SceneState.INACTIVE
        assert SceneState.LOADING
        assert SceneState.ACTIVE
        assert SceneState.PAUSED
        assert SceneState.TRANSITIONING
        assert SceneState.UNLOADING

    def test_scene_state_transitions_validity(self) -> None:
        """Test validità delle transizioni di stato"""
        scene = Scene[str]("test_scene")

        # Testa transizioni valide
        scene.on_enter()
        assert scene.state == SceneState.ACTIVE

        scene.on_pause()
        assert scene.state == SceneState.PAUSED  # type: ignore[comparison-overlap]

        scene.on_resume()
        assert scene.state == SceneState.ACTIVE

        scene.on_exit()
        assert scene.state == SceneState.INACTIVE


if __name__ == "__main__":
    # Inizializza pygame per i test
    pygame.init()

    # Esegui i test
    pytest.main([__file__, "-v"])

    pygame.quit()
