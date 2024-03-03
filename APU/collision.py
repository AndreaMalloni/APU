import threading

import pygame

from APU.scene import Scene

COLLISION_EVENT = pygame.USEREVENT + 1


def check_collision(sprite1, sprite2):
    # Controllo delle collisioni tra le hitbox dei due sprite
    for hitbox1_name, hitbox1 in sprite1.hitboxes.items():
        for hitbox2_name, hitbox2 in sprite2.hitboxes.items():
            if hitbox1.colliderect(hitbox2):
                # Collisione rilevata, emetti un evento COLLISION
                pygame.event.post(pygame.event.Event(COLLISION_EVENT, {
                    'sprite1': sprite1,
                    'sprite2': sprite2,
                    'hitbox1_name': hitbox1_name,
                    'hitbox2_name': hitbox2_name
                }))


class CollisionDetector:
    def __init__(self, scene: Scene):
        self.threads = None
        self.scene = scene
        self.running = False

    def check_collisions(self, target_sprite):
        while self.running:
            for sprite in self.scene:
                if sprite != target_sprite:
                    check_collision(target_sprite, sprite)

    def start(self):
        if not self.running:
            self.running = True
            self.threads = []

            for target_sprite in self.scene:
                # Avvia un thread separato per ciascun sprite
                collision_thread = threading.Thread(target=self.check_collisions, args=(target_sprite,))
                collision_thread.daemon = True  # Il thread si chiuderà quando il programma principale si chiude
                collision_thread.start()
                self.threads.append(collision_thread)

    def stop(self):
        if self.running:
            self.running = False
            for thread in self.threads:
                thread.join()  # Aspetta che tutti i thread terminino

    def pause(self, time):
        pass
