import pygame as pg
from APU.core.config import D_WIDTH, D_HEIGHT, ASSETSPATH, NORTH, EAST, SOUTH, WEST, DEFAULT_FPS, KEYMAP
from APU.entityObject import EntityObject
from APU.core.spritesheet import Spritesheet, SpriteStripAnim
from APU.core.font import Font
from APU.tiledMap import TiledMap
from APU.camera import YSortCameraGroup, LayeredCameraGroup
from APU.utility import deltaT, tmxRectToPgRect
from time import perf_counter

pg.init()    

window = pg.display.set_mode((D_WIDTH, D_HEIGHT), flags = pg.SCALED | pg.RESIZABLE, vsync = 0)
clock = pg.time.Clock()
font = Font(f"{ASSETSPATH}\large_font.png", (0, 0, 0))
mapObject = TiledMap(f"{ASSETSPATH}\dungeon - large.tmx")
walls = mapObject.getObjectsByName("wall")
#wallsRect = [tmxRectToPgRect(wall) for wall in walls]

cameraGroup = YSortCameraGroup(0, 0, window.get_size())
cameraGroup.add(mapObject.toSpriteGroupLoose())
cameraGroup.add(walls)

player = EntityObject(
    x = window.get_size()[0]/2 - 8, 
    y = window.get_size()[1]/2 - 8,
    speed = 3,
    layer = 1,
    defaultSpriteImage = Spritesheet(f"{ASSETSPATH}\Sprite-0001.png").image_at((0, 0, 16, 16), (0, 0, 0)),
    idle_front = SpriteStripAnim(f"{ASSETSPATH}\Sprite-0001.png", (0, 0, 16, 16), 3, (0, 0, 0), True, DEFAULT_FPS/10),
    idle_back = SpriteStripAnim(f"{ASSETSPATH}\Sprite-0001.png", (0, 16, 16, 16), 3, (0, 0, 0), True, DEFAULT_FPS/10),
    idle_right = SpriteStripAnim(f"{ASSETSPATH}\Sprite-0001.png", (0, 32, 16, 16), 3, (0, 0, 0), True, DEFAULT_FPS/10),
    idle_left = SpriteStripAnim(f"{ASSETSPATH}\Sprite-0001.png", (0, 48, 16, 16), 3, (0, 0, 0), True, DEFAULT_FPS/10),
    walk_front = SpriteStripAnim(f"{ASSETSPATH}\Sprite-0001.png", (0, 64, 16, 16), 3, (0, 0, 0), True, DEFAULT_FPS/10),
    walk_back = SpriteStripAnim(f"{ASSETSPATH}\Sprite-0001.png", (0, 80, 16, 16), 3, (0, 0, 0), True, DEFAULT_FPS/10),
    walk_right = SpriteStripAnim(f"{ASSETSPATH}\Sprite-0001.png", (0, 96, 16, 16), 3, (0, 0, 0), True, DEFAULT_FPS/10),
    walk_left = SpriteStripAnim(f"{ASSETSPATH}\Sprite-0001.png", (0, 112, 16, 16), 3, (0, 0, 0), True, DEFAULT_FPS/10),
    defaultSeq = "idle_front"
    )

directions = []
pg.display.set_caption("Demo")
run = True
last_time = perf_counter()
font.changeColor((255, 0, 0), (127, 127, 127))
cameraGroup.add(player)
cameraGroup.setMode(0, player)
        
fullscreen = False
toggleWall = False

while run:
    clock.tick(2000)
    dt, last_time = deltaT(last_time)

    for event in pg.event.get():
        if event.type == pg.QUIT:
            run = False
        if event.type == pg.KEYDOWN and event.key in KEYMAP:
            directions.append(KEYMAP[event.key])
        if event.type == pg.KEYUP and event.key in KEYMAP and KEYMAP[event.key] in directions:
            directions.remove(KEYMAP[event.key])
        if event.type == pg.KEYDOWN:
            if event.key == pg.K_f:
                if fullscreen: window = pg.display.set_mode((D_WIDTH, D_HEIGHT), flags=pg.SCALED | pg.RESIZABLE, vsync=0)  
                else: pg.display.set_mode((D_WIDTH, D_HEIGHT), flags=pg.SCALED | pg.FULLSCREEN, vsync=1)
                fullscreen = not fullscreen
            if event.key == pg.K_t:
                toggleWall = not toggleWall

    player.move(directions, dt)

    if not player.isMoving:
        if player.facingDirection == NORTH and player.currentAnimationSequence != "idle_back":
            player.switchTo("idle_back")
        if player.facingDirection == EAST and player.currentAnimationSequence != "idle_right":
            player.switchTo("idle_right")
        if player.facingDirection == SOUTH and player.currentAnimationSequence != "idle_front":
            player.switchTo("idle_front")
        if player.facingDirection == WEST and player.currentAnimationSequence != "idle_left":
            player.switchTo("idle_left")
    else:
        if player.facingDirection == SOUTH  and player.currentAnimationSequence != "walk_front":
            player.switchTo("walk_front")
        if player.facingDirection == EAST  and player.currentAnimationSequence != "walk_right":
            player.switchTo("walk_right")
        if player.facingDirection == NORTH  and player.currentAnimationSequence != "walk_back":
            player.switchTo("walk_back")
        if player.facingDirection == WEST  and player.currentAnimationSequence != "walk_left":
            player.switchTo("walk_left")
        

    window.fill((0, 0, 0))
    cameraGroup.customUpdate()
    cameraGroup.customDraw(window)
    
    if toggleWall:
        for wall in walls:
            pg.draw.rect(window, (127, 127, 127), wall.rect)

    font.render(window, str(int(clock.get_fps())), (5, 5))

    pg.display.flip()

