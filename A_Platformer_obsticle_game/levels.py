from sprites import *
from game_settings import *

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
        spew_fire = False
        if j % 3 == 0:
            spew_fire = True
        else:
            spew_fire = False

        lava = Lava(plat.rect.x + (initial_platform.get_size() * j), plat.rect.y - 5, game, spew_fire)
        Platform(lava.rect.x, lava.rect.y + initial_platform.get_size(False), game)
        Platform(lava.rect.x, lava.rect.y + 2*initial_platform.get_size(False), game, False) #Concrete platform

        if j % 3 == 0:
            Platform(lava.rect.x + 25, lava.rect.y - 2*initial_platform.get_size(False), game)

    first_stair_plat = Platform(lava.rect.x + initial_platform.get_size(False), plat.rect.y + 2, game)
    for k in range(4):
        Platform(first_stair_plat.rect.x + (initial_platform.get_size() * k - 5), first_stair_plat.rect.y + (15 * k), game)


def level_6(initial_platform, game):
    """Swordchopper level"""
    for i in range(4):
        Platform(WIDTH + 150 + (initial_platform.get_size() * i), BOTTOM_PLATFORM_Y_COORDINATE, game)
        high_mob_plat = Platform(WIDTH + 750 + (initial_platform.get_size() * i), -600, game)
        Platform(WIDTH + 450 + (initial_platform.get_size() * i), HEIGHT / 2, game)
        mob_plat = Platform(WIDTH + WIDTH * 3/4 - 120 + (initial_platform.get_size() * i), BOTTOM_PLATFORM_Y_COORDINATE, game)
        plat_length = 4 * initial_platform.get_size()

    for i in range(1, 3):
        Platform(WIDTH + 300 + (initial_platform.get_size() * i), HEIGHT / 2 + 100, game)

    SwordChopper(high_mob_plat, plat_length, 2, game) #Swordchopper that falls of the platforms
    SwordChopper(mob_plat, plat_length, 2, game, False, 1.5) #Swordchopper that stays on the platforms


def level_7(initial_platform, game):
    """New level copy paste from test level snow and hidden bombs"""
    Platform(WIDTH + 5, 200, game) #A reminder platform to show where the width of the screen is 
                                                #When to display the next level



        
    





    







    


