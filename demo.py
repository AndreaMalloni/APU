import pygame as pg
from APU.core.config import D_WIDTH, D_HEIGHT, ASSETSPATH, NORTH, EAST, SOUTH, WEST, DEFAULT_FPS, KEYMAP
from APU.entityObject import EntityObject
from APU.globalObjectGroup import GlobalObjectGroup
from APU.core.spritesheet import Spritesheet, SpriteStripAnim
from APU.core.font import Font
from APU.utility import deltaT
from time import perf_counter

pg.init()

window = pg.display.set_mode((D_WIDTH, D_HEIGHT), flags = pg.SCALED | pg.RESIZABLE, vsync = 1)
clock = pg.time.Clock()
font = Font(f"{ASSETSPATH}\large_font.png", (0, 0, 0))
blitSurface = pg.Surface((512, 288))
gameObjects = GlobalObjectGroup()

player = EntityObject(
    x = 100, 
    y = 100,
    defaultSpriteImage = Spritesheet(f"{ASSETSPATH}\Sprite-0001.png").image_at((0, 0, 16, 16), (0, 0, 0)),
    idle_front = SpriteStripAnim(f"{ASSETSPATH}\Sprite-0001.png", (0, 0, 16, 16), 3, (0, 0, 0), True, DEFAULT_FPS/10),
    idle_back = SpriteStripAnim(f"{ASSETSPATH}\Sprite-0001.png", (0, 16, 16, 16), 3, (0, 0, 0), True, DEFAULT_FPS/10),
    idle_right = SpriteStripAnim(f"{ASSETSPATH}\Sprite-0001.png", (0, 32, 16, 16), 3, (0, 0, 0), True, DEFAULT_FPS/10),
    idle_left = SpriteStripAnim(f"{ASSETSPATH}\Sprite-0001.png", (0, 48, 16, 16), 3, (0, 0, 0), True, DEFAULT_FPS/10),
    defaultSeq = "idle_front"
    )

directions = []
pg.display.set_caption("Demo")
run = True
last_time = perf_counter()
font.changeColor((255, 0, 0), (127, 127, 127))
gameObjects.add(player)

while run:
    clock.tick(DEFAULT_FPS)
    dt, last_time = deltaT(last_time)
    
    for event in pg.event.get():
        if event.type == pg.QUIT:
            run = False
        if event.type == pg.WINDOWRESIZED:
            D_WIDTH, D_HEIGHT = max(window.get_size()[0], 1280), max(window.get_size()[1], 720)
        if event.type == pg.KEYDOWN and event.key in KEYMAP:
            directions.append(KEYMAP[event.key])
        if event.type == pg.KEYUP and event.key in KEYMAP:
            directions.remove(KEYMAP[event.key])

    player.move(directions, dt)

    if player.isMoving:
        if player.movingDirection == NORTH:
            player.switchTo("idle_back")
        if player.movingDirection == EAST:
            player.switchTo("idle_right")
        if player.movingDirection == SOUTH:
            player.switchTo("idle_front")
        if player.movingDirection == WEST:
            player.switchTo("idle_left")
    '''
    else:       
        if player.facingDirection == NORTH:
            player.switchTo("idle_back")
        if player.facingDirection == EAST:
            player.switchTo("idle_right")
        if player.facingDirection == SOUTH:
            player.switchTo("idle_front")
        if player.facingDirection == WEST:
            player.switchTo("idle_left")
    '''

    blitSurface.fill((0, 0, 0))
    gameObjects.draw(blitSurface)
    font.render(blitSurface, str(int(clock.get_fps())), (5, 5))
    window.blit(pg.transform.scale(blitSurface, (D_WIDTH, D_HEIGHT)), (0,0))

    gameObjects.update()
    pg.display.update()

