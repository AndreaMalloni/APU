# import threading

from __future__ import annotations

from typing import TYPE_CHECKING

import pygame
from typing_extensions import override

if TYPE_CHECKING:
    from apu.objects.components import SolidBodyComponent

# from APU.scene import Scene

# COLLISION_EVENT = pygame.USEREVENT + 1


# def check_collision(sprite1, sprite2):
#     # Controllo delle collisioni tra le hitbox dei due sprite
#     for hitbox1_name, hitbox1 in sprite1.hitboxes.items():
#         for hitbox2_name, hitbox2 in sprite2.hitboxes.items():
#             if hitbox1.colliderect(hitbox2):
#                 # Collisione rilevata, emetti un evento COLLISION
#                 pygame.event.post(pygame.event.Event(COLLISION_EVENT, {
#                     'sprite1': sprite1,
#                     'sprite2': sprite2,
#                     'hitbox1_name': hitbox1_name,
#                     'hitbox2_name': hitbox2_name
#                 }))


# class CollisionDetector:
#     def __init__(self, scene: Scene):
#         self.threads = None
#         self.scene = scene
#         self.running = False

#     def check_collisions(self, target_sprite):
#         while self.running:
#             for sprite in self.scene:
#                 if sprite != target_sprite:
#                     check_collision(target_sprite, sprite)

#     def start(self):
#         if not self.running:
#             self.running = True
#             self.threads = []

#             for target_sprite in self.scene:
#                 # Avvia un thread separato per ciascun sprite
#                 collision_thread = threading.Thread(
#                     target=self.check_collisions,
#                     args=(target_sprite,)
#                 )
#                 collision_thread.daemon = True
#                 collision_thread.start()
#                 self.threads.append(collision_thread)

#     def stop(self):
#         if self.running:
#             self.running = False
#             for thread in self.threads:
#                 thread.join()  # Aspetta che tutti i thread terminino

#     def pause(self, time):
#         pass


class HitBox:
    def __init__(self, rect: pygame.rect.Rect, visible: bool = False) -> None:
        self._body: SolidBodyComponent | None = None
        self.rect = rect
        self.visible = visible
        self.border_width = 1
        self.border_color = (255, 0, 0)

    def absolute_rect(self, offset: tuple[int, int]) -> pygame.Rect:
        """Returns an offsetted rect object, based on the entity position."""
        return self.rect.move(offset)

    def draw(self, surface: pygame.surface.Surface) -> None:
        if self.visible and self._body is not None and self._body.entity is not None:
            pygame.draw.rect(
                surface,
                self.border_color,
                self.absolute_rect(self._body.entity.position),
                width=self.border_width,
            )

    @override
    def __str__(self) -> str:
        return f"""
        Rect: {self.rect} 
        Visible: {self.visible} 
        Border width: {self.border_width} 
        Border color: {self.border_color} 
        """
