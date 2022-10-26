import pygame as pg
from pathlib import Path
from APU.core.config import D_WIDTH, D_HEIGHT, ASSETSPATH, NORTH, EAST, SOUTH, WEST, IDLE
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
    defaultSpriteImage = Spritesheet(f"{ASSETSPATH}\Sprite-0001.png").image_at((0, 0, 16, 16), (0, 0, 0)), 
    idle_front = SpriteStripAnim(f"{ASSETSPATH}\Sprite-0001.png", (0, 0, 16, 16), 3, (0, 0, 0), True, 6),
    idle_back = SpriteStripAnim(f"{ASSETSPATH}\Sprite-0001.png", (0, 16, 16, 16), 3, (0, 0, 0), True, 6),
    idle_right = SpriteStripAnim(f"{ASSETSPATH}\Sprite-0001.png", (0, 32, 16, 16), 3, (0, 0, 0), True, 6),
    idle_left = SpriteStripAnim(f"{ASSETSPATH}\Sprite-0001.png", (0, 48, 16, 16), 3, (0, 0, 0), True, 6)
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

    if player.isMoving:
        if player.movingDirection == NORTH:
            player.switchTo("idle_back")
        if player.movingDirection == EAST:
            player.switchTo("idle_right")
        if player.movingDirection == SOUTH:
            player.switchTo("idle_front")
        if player.movingDirection == WEST:
            player.switchTo("idle_left")
    else:
        pass
        '''
        if player.facingDirection == NORTH:
            player.switchTo("idle_back")
        if player.facingDirection == EAST:
            player.switchTo("idle_right")
        if player.facingDirection == SOUTH:
            player.switchTo("idle_front")
        if player.facingDirection == WEST:
            player.switchTo("idle_left")
        '''


    blitSurface.fill((255,255,255))
    gameObjects.draw(blitSurface)
    window.blit(pg.transform.scale(blitSurface, (D_WIDTH, D_HEIGHT)), (0,0))
    window.blit(clockToSurfaceFPS(clock, font), (10,0))

    gameObjects.update()     
    pg.display.update()

