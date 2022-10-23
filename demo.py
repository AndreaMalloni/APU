import pygame as pg
from pathlib import Path
from APU.core.constants import D_WIDTH, D_HEIGHT, ASSETSPATH
from APU.entityObject import EntityObject
from APU.globalObjectGroup import GlobalObjectGroup
from APU.core.spritesheet import Spritesheet, SpriteStripAnim
from APU.utility import getDirectionFromKeymap, clockToSurfaceFPS

pg.init()

clock = pg.time.Clock()
font = pg.font.SysFont("Arial", 18)

window = pg.display.set_mode((D_WIDTH, D_HEIGHT), pg.RESIZABLE)
pg.display.set_caption("Shooter")

run = True
blitSurface = pg.Surface((512, 288))

player = EntityObject(
    100, 
    100,
    defaultSpriteImage = Spritesheet(f"{ASSETSPATH}\Sprite-0001.png").image_at((0, 0, 16, 16)).convert(), 
    idle_front = SpriteStripAnim(f"{ASSETSPATH}\Sprite-0001.png", (0, 0, 16, 16), 3, True, 6),
    idle_back = SpriteStripAnim(f"{ASSETSPATH}\Sprite-0001.png", (0, 16, 16, 32), 3, True, 6),
    idle_right = SpriteStripAnim(f"{ASSETSPATH}\Sprite-0001.png", (0, 32, 16, 48), 3, True, 6),
    idle_left = SpriteStripAnim(f"{ASSETSPATH}\Sprite-0001.png", (0, 48, 16, 64), 3, True, 6)
    )

gameObjects = GlobalObjectGroup()
gameObjects.add(player)

while run:
    clock.tick(60)

    for event in pg.event.get():
        if event.type == pg.QUIT:
            run = False
        if event.type == pg.WINDOWRESIZED:
            D_WIDTH, D_HEIGHT = window.get_size()

    keys = pg.key.get_pressed()
    player.move(getDirectionFromKeymap(keys))
    blitSurface.fill((255,255,255))
    gameObjects.draw(blitSurface)
    window.blit(pg.transform.scale(blitSurface, (D_WIDTH, D_HEIGHT)), (0,0))
    gameObjects.update()

    window.blit(clockToSurfaceFPS(clock, font), (10,0))   
    pg.display.flip()

