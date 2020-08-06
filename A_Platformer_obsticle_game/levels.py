from sprites import *
from game_settings import *
from trap_sprites import *
from enemy_sprites import *
from fire_sprites import *
from one_frame_sprites import GoldPile

SPIKE_NO_ANIMATION_HEIGHT_MARGIN = 40
SPIKE_NO_ANIMATION_WIDTH_MARGIN = 42

"""Functions for blitting the next levels"""
def opening_level_part2(initial_platform, game):
    for i in range(4):
        Platform(WIDTH + 50 + (initial_platform.get_size() * i), HEIGHT - 150, game)
        Platform(WIDTH + 300 + (initial_platform.get_size() * i), HEIGHT / 2, game)
        Platform(WIDTH + 600 + (initial_platform.get_size() * i), HEIGHT - 50, game)

    for j in range(2):
        SingleFrameSpriteTrap(WIDTH + 300 + SPIKE_NO_ANIMATION_WIDTH_MARGIN + (initial_platform.get_size() * j), HEIGHT / 2 - SPIKE_NO_ANIMATION_HEIGHT_MARGIN, game, False)


def level_1(initial_platform, game):
    """Level 1 and the opening level are together. 
    When the camera's x position reaches WIDTH - 50 
    the next level is blit on the window with the coordinates 
    x = WIDTH + some number, y = some number"""

    SingleFrameSpriteTrap(WIDTH - 200, -30, game, True, False, True)

    for i in range(24):
        if 17 <= i <= 19:
            if i == 18 or i == 19:
                Lava(WIDTH + (initial_platform.get_size() * i), BOTTOM_PLATFORM_Y_COORDINATE, game, True)
            else:
                Lava(WIDTH + (initial_platform.get_size() * i), BOTTOM_PLATFORM_Y_COORDINATE, game, False)
        else:
            Platform(WIDTH + (initial_platform.get_size() * i), BOTTOM_PLATFORM_Y_COORDINATE, game)
    
    #Spawn an axes
    SingleFrameSpriteTrap(WIDTH + 300, 70, game, True, False, False, True)
    SingleFrameSpriteTrap(WIDTH + 500, 10, game, True, False, False, True)

def level_2(initial_platform, game):
    #Spawn a boulder
    SingleFrameSpriteTrap(WIDTH + 200, HEIGHT / 4 - 50, game, True, False, True)

    for i in range(3):
        Platform(WIDTH + 150 + (initial_platform.get_size() * i), HEIGHT / 2 + 100, game)

    #Spike animated platform in between the two longer platforms
    SingleFrameSpriteTrap(WIDTH + 200 + (initial_platform.get_size() * 3), HEIGHT / 2 + 200, game) 

    for j in range(1, 6):
        Platform(WIDTH + WIDTH / 3 + (initial_platform.get_size() * j), HEIGHT / 2 + 150, game)
    
    #Spike animating up and down
    for k in range(2, 5, 2):
        SingleFrameSpriteTrap(WIDTH + WIDTH / 3 + (initial_platform.get_size() * k), HEIGHT / 2 + 150, game, True) 

    SingleFrameSpriteTrap(WIDTH + WIDTH - 370, -HEIGHT / 2, game, True, False, False, True) #Animating axe

    counter = 0
    for x in range(16):
        if x > 10:
            counter += 1
            Platform(WIDTH + WIDTH - 400 + (initial_platform.get_size() * x), BOTTOM_PLATFORM_Y_COORDINATE - ((initial_platform.get_size(False) * counter) / 2 + 10), game)
        else:
            Platform(WIDTH + WIDTH - 400 + (initial_platform.get_size() * x), BOTTOM_PLATFORM_Y_COORDINATE, game)

def level_3(initial_platform, game):
    for j in range(5):
        plat = Platform(WIDTH + WIDTH / 2 + (initial_platform.get_size() * j) - 5, HEIGHT - 160, game)
        Platform(WIDTH + WIDTH * 3/4 + (initial_platform.get_size() * j) - 50, HEIGHT - 50, game)
    Snake(plat, game)

def level_4(initial_platform, game):
    for i in range(125, 251, 125):
        Platform(WIDTH + i + 150, HEIGHT - i, game)
        Platform(WIDTH + initial_platform.get_size() + i + 150, HEIGHT - i, game)
        plat = Platform(WIDTH + 2*initial_platform.get_size() + i + 150, HEIGHT - i, game)
        Platform(WIDTH + 3*initial_platform.get_size() + i + 150, HEIGHT - i, game)
        Platform(WIDTH + 4*initial_platform.get_size() + i + 150, HEIGHT - i, game)
        last_plat = Platform(WIDTH + 5*initial_platform.get_size() + i + 150, HEIGHT - i, game)
    Snake(plat, game)

    SingleFrameSpriteTrap(last_plat.rect.x + initial_platform.get_size(), last_plat.rect.y - SPIKE_NO_ANIMATION_HEIGHT_MARGIN, game, False)

    for i in range(1, 3):
        Platform(last_plat.rect.x + (initial_platform.get_size() * i) + 100, 250, game)

def level_5(initial_platform, game):
    """Small lava level"""
    
    plat = Platform(WIDTH + 70, HEIGHT / 2 + 100, game)
    Platform(plat.rect.x - initial_platform.get_size(), plat.rect.y, game)
        
    for j in range(1, 18):
        if j in [1, 2, 4, 8, 12, 16]:
            spew_fire = False 
        else:
            spew_fire = True

        lava = Lava(plat.rect.x + (initial_platform.get_size() * j), plat.rect.y - 5, game, spew_fire)
        Platform(lava.rect.x, lava.rect.y + initial_platform.get_size(False), game)
        Platform(lava.rect.x, lava.rect.y + 2*initial_platform.get_size(False), game, False, True) #Concrete platform

        if j % 4 == 0:
            Platform(lava.rect.x - 20, lava.rect.y - 2*initial_platform.get_size(False), game) #jump platforms

    first_stair_plat = Platform(lava.rect.x + initial_platform.get_size(False), plat.rect.y + 2, game)
    for k in range(4):
        Platform(first_stair_plat.rect.x + (initial_platform.get_size() * k - 5), first_stair_plat.rect.y + (15 * k), game)


def level_6(initial_platform, game):
    """Swordchopper level"""
    for i in range(4):
        Platform(WIDTH + 150 + (initial_platform.get_size() * i), BOTTOM_PLATFORM_Y_COORDINATE, game)
        high_mob_plat = Platform(WIDTH + 760 + (initial_platform.get_size() * i), -600, game)
        Platform(WIDTH + 450 + (initial_platform.get_size() * i), HEIGHT / 2, game)
        mob_plat = Platform(WIDTH + WIDTH * 3/4 - 120 + (initial_platform.get_size() * i), BOTTOM_PLATFORM_Y_COORDINATE, game)
        plat_length = 4 * initial_platform.get_size()

    for i in range(1, 3):
        Platform(WIDTH + 300 + (initial_platform.get_size() * i), HEIGHT / 2 + 100, game)

    SwordChopper(high_mob_plat, plat_length, 2.5, game) #Swordchopper that falls of the platforms
    SwordChopper(mob_plat, plat_length, 2, game, False, 1.5) #Swordchopper that stays on the platforms


def level_7(initial_platform, game):
    for i in range(6):
        if i == 3:
            bomb_plat = Platform(WIDTH + 110 + (initial_platform.get_size() * i), 300, game)
        grass_plat = Platform(WIDTH + 110 + (initial_platform.get_size() * i), 300, game) 

    for k in range(10): #10
        if k == 2:
            spawn_bomb_plat_snow = Platform(grass_plat.rect.x + 100 + (initial_platform.get_size() * k), HEIGHT / 2, game, False, False, True) #Snow platform
        Platform(grass_plat.rect.x + 100 + (initial_platform.get_size() * k), HEIGHT / 2, game, False, False, True) #Snow platform

    Bomb(bomb_plat, game)
    Bomb(spawn_bomb_plat_snow, game)
    

def initial_snow_level(initial_platform, game):
    SingleFrameSpriteTrap(WIDTH + 500, -500, game, True, False, False, True) #An axe for level_7 (hidden snow axe)

    """Level 8 starts here"""
    for i in range(15):
        if i == 7:
            bomb_plat = Platform(WIDTH + 50 + (initial_platform.get_size() * i), HEIGHT - 50, game, False, False, True)
        if i == 9:
            concrete_tower_plat = Platform(WIDTH + 50 + (initial_platform.get_size() * i), HEIGHT - 50, game, False, False, True)
        last_plat = Platform(WIDTH + 50 + (initial_platform.get_size() * i), HEIGHT - 50, game, False, False, True)

    #Do not forget to put (1, some range) otherwise a concrete plat will spawn inside the grass platform and will block Joe from walking forward
    for j in range(1, 8): 
        Platform(concrete_tower_plat.rect.x, concrete_tower_plat.rect.y - (initial_platform.get_size(False) * j), game, False, True)

    Bomb(bomb_plat, game, 2)

    for k in range(10):
        Platform(last_plat.rect.x + (initial_platform.get_size() * k), last_plat.rect.y - (initial_platform.get_size(False) / 2 * k), game, False, False, True)

def level_9(initial_platform, game):
    """A big bomb level with swordchoppers"""

    for i in range(9):
        snow_plat = Platform(WIDTH + 235 + (initial_platform.get_size() * i), HEIGHT / 2, game, False, False, True)
        if i % 2 == 0:
            if i == 8:
                Bomb(snow_plat, game) #last bomb is bigger than the other bombs
            else:
                Bomb(snow_plat, game, 2)
        else:
            for concrete_qty in range(4):
                top_concrete_plat = Platform(snow_plat.rect.x, snow_plat.rect.y - (initial_platform.get_size(False) * concrete_qty), game, False, True)
            SwordChopper(top_concrete_plat, 1, 2, game)

    last_bomb_plat = Platform(snow_plat.rect.x + initial_platform.get_size(), snow_plat.rect.y, game, False, False, True)

    for j in range(1, 5):
        Platform(last_bomb_plat.rect.x + (initial_platform.get_size() * j), last_bomb_plat.rect.y + 50, game, False, False, True)

def last_snow_level(initial_platform, game):
    for i in range(4):
        Platform(WIDTH - 10 + (initial_platform.get_size() * i), BOTTOM_PLATFORM_Y_COORDINATE, game)

    for i in range(5):
        Platform(WIDTH + 200 + (initial_platform.get_size() * i), HEIGHT - 100, game, False, False, True)
        mid_plat = Platform(WIDTH + 450 + (initial_platform.get_size() * i), HEIGHT - 150, game, False, False, True)
        plat = Platform(WIDTH + 700 + (initial_platform.get_size() * i), HEIGHT - 200, game, False, False, True)
        if i == 2: 
            Bomb(plat, game, 1)
        if i == 3 or i == 4:
            for up in range(1,7):
                Platform(plat.rect.x, plat.rect.y - (initial_platform.get_size() * up), game, False, True)
        if i == 3:
            Bomb(mid_plat, game)

    SwordChopper(mid_plat, initial_platform.get_size() * 5, 2, game, False)

def level_11(initial_platform, game):
    for down in range(8):
        last_plat = Platform(WIDTH + 90 + (initial_platform.get_size() * down), 300 + (initial_platform.get_size(False) / 2 * down), game)

    for x in range(1, 11):
        Platform(last_plat.rect.x + (initial_platform.get_size() * x), BOTTOM_PLATFORM_Y_COORDINATE, game)

def castle_level(initial_platform, game):
    """Castle gate level (need assets for a 
    castle gate, tresure chest, trigger(kill the minotaur), 
    cannon for the axe and the boulder"""

    for i in range(20):
        if i == 0:
            snake_plat = Platform(WIDTH + (initial_platform.get_size() * i), BOTTOM_PLATFORM_Y_COORDINATE, game)
        if i == 9:
            cannon_plat = Platform(WIDTH + (initial_platform.get_size() * i), BOTTOM_PLATFORM_Y_COORDINATE, game)
        if i == 13:
            start_castle_plat = Platform(WIDTH + (initial_platform.get_size() * i), BOTTOM_PLATFORM_Y_COORDINATE, game)
        if i == 16:
            castle_door_plat = Platform(WIDTH + (initial_platform.get_size() * i), BOTTOM_PLATFORM_Y_COORDINATE, game)
        Platform(WIDTH + (initial_platform.get_size() * i), BOTTOM_PLATFORM_Y_COORDINATE, game)

    Cannon(cannon_plat, game)
    Snake(snake_plat, game)


    #The castle 
    for row in range(7):
        for col in range(5):
            top_castle_plat = Platform(start_castle_plat.rect.x + (initial_platform.get_size() * row - 34), start_castle_plat.rect.y - initial_platform.get_size(False) - (initial_platform.get_size() * col), game, False, True, False, True) #transparent concrete platform for the castle building. 34 is a random width margin
        if row % 2 == 0:
            Platform(top_castle_plat.rect.x, top_castle_plat.rect.y - initial_platform.get_size(False), game, False, True, False, True)

    #This syntax is known as a function attribute, because functions in python are treated like an object
    castle_level.door = CastleDoor(castle_door_plat.rect.x - 10, castle_door_plat.rect.y, game) 

def boss_level(initial_platform, game):
    """Here starts the boss level (red minotaur level)"""
    for i in range(19):
        if i in [num for num in range(13, 19)]: 
            if i == 15:
                golden_pile_plat = Platform(WIDTH + 50 + (initial_platform.get_size() * i), BOTTOM_PLATFORM_Y_COORDINATE - initial_platform.get_size() // 2, game)
            last_plat = Platform(WIDTH + 50 + (initial_platform.get_size() * i), BOTTOM_PLATFORM_Y_COORDINATE - initial_platform.get_size() // 2, game)
        else:
            """Boss platforms"""
            if i == 10:
                boss_spawn_plat = Platform(WIDTH + 50 + (initial_platform.get_size() * i), BOTTOM_PLATFORM_Y_COORDINATE - initial_platform.get_size(), game)
                game.boss_platforms_list.append(boss_spawn_plat)

            boss_death_plat = Platform(WIDTH + 50 + (initial_platform.get_size() * i), BOTTOM_PLATFORM_Y_COORDINATE - initial_platform.get_size(), game)
            game.boss_platforms_list.append(boss_death_plat)

    for up in range(12):
        if up == 5:
            switch_wall_plat = Platform(last_plat.rect.x, last_plat.rect.y - (initial_platform.get_size(False) * up), game, False, True) #concrete wall
        Platform(last_plat.rect.x, last_plat.rect.y - (initial_platform.get_size(False) * up), game, False, True) #concrete wall

    GoldPile(golden_pile_plat, game)
    DeathSwitch(switch_wall_plat, game)
    MinotaurBoss(boss_spawn_plat, game)
