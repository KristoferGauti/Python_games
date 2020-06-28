from sprites import *
from game_settings import *

SPIKE_NO_ANIMATION_HEIGHT_MARGIN = 40
SPIKE_NO_ANIMATION_WIDTH_MARGIN = 42

"""Functions for blitting the next levels"""
def opening_level_part2(main_player, initial_platform, game):
    for i in range(4):
        Platform(WIDTH + 50 + (initial_platform.get_size() * i), HEIGHT - 150, game)
        Platform(WIDTH + 300 + (initial_platform.get_size() * i), HEIGHT / 2, game)
        Platform(WIDTH + 600 + (initial_platform.get_size() * i), HEIGHT - 50, game)

    for j in range(2):
        SingleFrameSpriteTrap(WIDTH + 300 + SPIKE_NO_ANIMATION_WIDTH_MARGIN + (initial_platform.get_size() * j), HEIGHT / 2 - SPIKE_NO_ANIMATION_HEIGHT_MARGIN, game, False)


def level_1(main_player, initial_platform, game):
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

def level_2(main_player, initial_platform, game):
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

def level_3(main_player, initial_platform, game):
    for j in range(5):
        plat = Platform(WIDTH + WIDTH / 2 + (initial_platform.get_size() * j) - 5, HEIGHT - 160, game)
        Platform(WIDTH + WIDTH * 3/4 + (initial_platform.get_size() * j) - 50, HEIGHT - 50, game)


    for i in range(125, 251, 125):
        Platform(2*WIDTH + i, HEIGHT - i, game)
        Platform(2*WIDTH + initial_platform.get_size() + i, HEIGHT - i, game)
        sec_plat = Platform(2*WIDTH + 2*initial_platform.get_size() + i, HEIGHT - i, game)
        Platform(2*WIDTH + 3*initial_platform.get_size() + i, HEIGHT - i, game)
        Platform(2*WIDTH + 4*initial_platform.get_size() + i, HEIGHT - i, game)


    Platform(WIDTH + WIDTH - 60, HEIGHT - 150, game)
    Platform(WIDTH + WIDTH - 60 + initial_platform.get_size(), HEIGHT - 150, game)

    Snake(plat, game)
    Snake(sec_plat, game)
        
    





    







    


