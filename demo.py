import pygame as pg
from APU.core.config import D_WIDTH, D_HEIGHT, ASSETSPATH, NORTH, EAST, SOUTH, WEST, DEFAULT_FPS, KEYMAP
from APU.entityObject import EntityObject
from APU.core.spritesheet import Spritesheet, SpriteStripAnim
from APU.core.font import Font
from APU.tiledMap import TiledMap
from APU.utility import deltaT
from time import perf_counter

pg.init()

window = pg.display.set_mode((D_WIDTH, D_HEIGHT), flags = pg.SCALED | pg.RESIZABLE, vsync = 0)
clock = pg.time.Clock()
font = Font(f"{ASSETSPATH}\large_font.png", (0, 0, 0))
mapObject = TiledMap(f"{ASSETSPATH}\dungeon.tmx")
#layeredMap = mapObject.toLayeredGroupLoose()
layeredMap = mapObject.toLayeredGroupCompact()
gameObjects = mapObject.getObjectsByLayerName("gameObjects")
walls = mapObject.getObjectsByName("wall")

player = EntityObject(
    x = mapObject.tmxMapObject.get_object_by_name("spawn").x, 
    y = mapObject.tmxMapObject.get_object_by_name("spawn").y,
    speed = 3,
    layer = 1,
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
layeredMap.add(player)

while run:
    clock.tick(2000)
    dt, last_time = deltaT(last_time)
    
    for event in pg.event.get():
        if event.type == pg.QUIT:
            run = False
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
    window.fill((0, 0, 0))

    layeredMap.draw(window)
    font.render(window, str(int(clock.get_fps())), (5, 5))

    layeredMap.update()
    pg.display.update()

