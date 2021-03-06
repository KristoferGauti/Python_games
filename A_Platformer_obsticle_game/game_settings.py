import pygame

#pygame basic variables stuff
TITLE = "Adventurous Joe"
WIDTH, HEIGHT = 1100, 500
CLOCK = pygame.time.Clock()
FPS = 60
FONT = "comicsans" 

#pygame init stuff
WIN = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.font.init()
pygame.mixer.init()
pygame.display.set_caption("Adventurous Joe")

#Layers
PLATFORM_LAYER = 3
CASTLE_DOOR_LAYER = 4
CANNON_LAYER = 2
SNOW_LAYER = 5
LAVA_LAYER = 3
MAIN_CHARACTER_LAYER = 5
TRAP_LAYER = 2
FIREBALL_LAYER = 2
TITLE_LAYER = 2
PIXEL_SIGN_LAYER = 3
ENEMY_LAYER = 2
GOLD_PILE_LAYER = 3
DEATH_SWITCH_LAYER = 3
BGLAYER = 1
TORCH_LAYER = 2

#Main character's and enemy's properties
GRAVITY = 0.8
SNOW_GRAVITY = 0.0849320
ACCELERATION = 0.345 
PLAYER_JUMP = -18
FRICTION = -0.07 

#Minotaur boss properties
MINOTAUR_GRAVITY = 0.2
MINOTAUR_POWER_JUMP = -13
MINOTAUR_SMALL_JUMP = -6

#Colors
BLACK = (0, 0, 0)
WHITE = (255, 255, 255)
SKYBLUE = (75, 156, 211)
DEATHBGCOLOR = (102,0,0) 
BUTTON_COLOR = (139, 69, 19)
SPRITESHEET_BG_SURFACE_COLOR = (10, 10, 10) #black-ish color

#traps properties
SPIKE_HEIGHT = 40
LAVA_BALL_FRICTION = -0.09

#Additional constants
CAMERA_FOCUSPOINT_X_POS = 230 #Can change to 130 otherwise do not change this constant
BOTTOM_PLATFORM_Y_COORDINATE = HEIGHT - 40

