"""Author: Kristofer Gauti"""
"""Adventurous Joe is an obsticle game which was inspired by Super Mario"""

"""Enemy sprites are from https://szadiart.itch.io/animated-character-pack?download"""
"""Main character is from https://jesse-m.itch.io/jungle-pack"""
"""The traps are from https://opengameart.org/content/animated-traps-and-obstacles"""

"""TODO: Camera system - Done
         code snow levels - Done
         Implement a death counter - Done
         code a castle enterance with the cannon and axe cannon - Doing
         in the castle is the boss level (minotour level)
         code backgrounds and visuals (snow falling down in the snow level and more)
"""

import pygame
import random
import os
from time import sleep

from game_settings import *
from sprites import *
from levels import *

class Game():
    def __init__(self, death_counter):
        self.running = True
        self.playing = True
        self.run_once_sign = True
        self.run_once_death_counter = True
        self.main_player_can_move = True
        self.draw_level = True
        self.reset_camera = False
        self.dead = False
        self.display_key_input_instructions = False
        self.display_bigger_sign = False
        self.play_dead_sound = True
        self.__dirname = os.path.dirname(__file__)
        self.__sound_dir = os.path.join(self.__dirname, "sounds")
        self.spritesheet_dir = os.path.join(self.__dirname, "spritesheet")
        self.game_over_text = ""
        self.camera_movement_x_coordinate = CAMERA_FOCUSPOINT_X_POS
        self.all_sprites = pygame.sprite.LayeredUpdates()
        self.platforms = pygame.sprite.Group()
        self.lavas = pygame.sprite.Group()
        self.fireballs = pygame.sprite.Group()
        self.traps = pygame.sprite.Group() 
        self.sign = pygame.sprite.Group()
        self.enemies = pygame.sprite.Group() 
        self._load_data()
        self.level_index = 0
        self.death_counter = death_counter
        self.levels = [level_10, level_11, level_12, opening_level_part2, level_1, level_2, level_3, level_4, level_5, level_6, level_7, level_8, level_9, level_10, level_11]
  
    def _load_data(self):
        self.main_sprite_sheet = SpritesheetParser(os.path.join(self.spritesheet_dir, "enemies_maincharacter_spritesheet.png"))
        self.traps_sprite_sheet = SpritesheetParser(os.path.join(self.spritesheet_dir, "traps_rip_joe_spritesheet.png"))
        self.title_boss_sprite_sheet = SpritesheetParser(os.path.join(self.spritesheet_dir, "title_sign_boss_spritesheet.png"))

        #load sounds 
        self.scream_sound = pygame.mixer.Sound(os.path.join(self.__sound_dir, "man_scream.wav"))
        self.burning_sound = pygame.mixer.Sound(os.path.join(self.__sound_dir, "burning.wav"))
        self.ohh_sound = pygame.mixer.Sound(os.path.join(self.__sound_dir, "classic_hurt.wav"))

    def events(self):
        """Event handlers"""

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                quit()

            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    quit()

                if self.main_player_can_move:
                    if event.key == pygame.K_SPACE: #for jumping
                        self.main_player.jump()
                else:
                    pass

                if event.key == pygame.K_r: #key check for reading the opening level sign
                    self.main_player.velocity.x = 0
                    self.run_once_sign = True
                    if self.display_key_input_instructions:
                        self.main_player_can_move = False
                        self.display_bigger_sign = True

                if event.key == pygame.K_b: #key check for stop reading the opening level sign
                    self.display_bigger_sign = False
                    self.main_player_can_move = True

                if self.dead:
                    if event.key == pygame.K_RETURN:
                        main(self.death_counter)

            if self.main_player_can_move:
                if event.type == pygame.KEYUP:
                    self.main_player.cut_jump()
            else:
                pass

    def _draw_text(self, x, y, text, font_size, color):
        font = pygame.font.SysFont(FONT, font_size)
        text_surface = font.render(text, 1, color)
        text_rect = text_surface.get_rect()
        text_rect.midtop = (x, y)
        WIN.blit(text_surface, text_rect)

    def _play_sound(self, wav_file):
        if isinstance(wav_file, list):
            if self.play_dead_sound: #Play the sound once
                wav_file[0].play()
                sleep(0.2) #from the time module
                wav_file[1].play()
                self.play_dead_sound = False
        else:
            if self.play_dead_sound: #play the sound once
                wav_file.play()
                self.play_dead_sound = False

    def _check_trap_hit(self, trap_hit_list, hits_platform):
        try:
            if trap_hit_list[0].spike:
                try:
                    if hits_platform[0].rect.top and trap_hit_list[0].spike_go_up:
                        self.game_over_text = "was stung to death"
                        return True
                    if (trap_hit_list[0].spike_go_down and trap_hit_list[0].rect.bottom or
                    trap_hit_list[0].spike_go_down and trap_hit_list[0].rect.left or
                    trap_hit_list[0].spike_go_down and trap_hit_list[0].rect.right):
                        return False

                except IndexError:
                    self.game_over_text = "was stung to death"
                    return True
                
            elif trap_hit_list[0].stone:
                self.game_over_text = "was hit by a boulder and died"
                return True

            elif trap_hit_list[0].axe:
                self.game_over_text = "was cut by an axe to death"
                return True

        except AttributeError:
            pass

    def move_main_player_camera(self):
        """Move the camera's focuspoint further to the right"""

        camera_speed = max(abs(int(self.main_player.velocity.x // 3)), 2) + 2
        if self.main_player.position.x >= CAMERA_FOCUSPOINT_X_POS:
            if self.reset_camera: #then reset the camera to the main_player's focuspoint
                self.camera_movement_x_coordinate = CAMERA_FOCUSPOINT_X_POS
                self.reset_camera = False
            else: #move the camera with respect to the main_player's velocity
                self.camera_movement_x_coordinate += camera_speed 

            #Check if the sprites goes off the screen. If so delete them from their groups  
            for sprite in self.all_sprites:
                sprite.rect.x -= camera_speed 
                if sprite.rect.right < 0:
                    sprite.kill()

            for lavaball in self.fireballs:
                lavaball.position.x -= camera_speed
                if lavaball.position.x + 50 < 0: #+50 so the enemy fades out, not disappear
                    lavaball.kill()
 
            for enemy in self.enemies:
                if enemy.type == "sword chopper":
                    enemy.position.x -= camera_speed
                    enemy.initial_x_position -= camera_speed
                    if enemy.position.x + 50 < 0 or enemy.position.y > HEIGHT + 50:
                        enemy.kill()

            self.main_player.position.x -= camera_speed 

    def change_level(self):
        """If the camera's x coordinate has reached the 
        width of the screen - 50 then blit the next level 
        and reset the camera to its initial x coordinate"""

        if self.camera_movement_x_coordinate == WIDTH - 50:
            print("Next level!")
            self.main_player.position.x += 5
            self.level_index += 1
            self.reset_camera = True
            self.draw_level = True

        #This function blits the upcomming next levels
        if self.draw_level: #draw the level once
            try:
                self.levels[self.level_index](self.grass_platform, self) #self.levels is a list containing functions of the levels in levels.py
            except IndexError:
                print("Index_error")
                #self.boss_level()

            self.draw_level = False

    def _adjust_player_platform_y_position(self, the_y_position):
        """This function adjusts the main_player's y position when 
        he jumps on a platform"""
        if self.main_player.position.y >= the_y_position:
            self.main_player.position.y = the_y_position
            self.main_player.velocity.y = 0
            self.main_player.jumping = False

    def _check_enemy_hit(self, enemy_list):
        """Checks which enemy was hit and sets the display 
        text corresponding to the enemy type"""

        for enemy in enemy_list:
            if enemy.type == "snake":
                self.game_over_text = "got eaten by snakes"
                return True
            if enemy.type == "sword chopper":
                self.game_over_text = "was chopped to death"
                return True
                
    def _game_over_functionality(self, sound_when_dead, gameover_text_str):
        """Sets the game over functionality and 
        calls the game over screen"""

        self._play_sound(sound_when_dead)
        self.dead = True
        self.game_over_text = gameover_text_str
        self.game_over_screen()

    def game_over_collision(self, hits_platform):
        """checks what object killed Joe with pygame mask collision 
        (pixel perfect collision) and calls the game over functionality 
        function to display the game over screen"""

        #Obsticle hit lists (mask collision -> pixel perfect collision)
        lava_hits = pygame.sprite.spritecollide(self.main_player, self.lavas, False, pygame.sprite.collide_mask)
        fireball_hits = pygame.sprite.spritecollide(self.main_player, self.fireballs, False, pygame.sprite.collide_mask)
        trap_hit = pygame.sprite.spritecollide(self.main_player, self.traps, False, pygame.sprite.collide_mask)
        enemy_hit = pygame.sprite.spritecollide(self.main_player, self.enemies, False, pygame.sprite.collide_mask)

        #Jumped into a lava, hit by the lava balls or hit by the traps (Fix this later, put in function)
        if lava_hits:
            self._game_over_functionality([self.ohh_sound, self.burning_sound], "was burned to death")
        if fireball_hits:
            self._game_over_functionality([self.ohh_sound, self.burning_sound], "was fireballed to death")
        if trap_hit:
            if self._check_trap_hit(trap_hit, hits_platform):
                self.dead = True
                self._play_sound(self.ohh_sound)
                self.game_over_screen()
            
        #Gotten hit by the enemies
        if enemy_hit:
            if self._check_enemy_hit(enemy_hit):
                self.dead = True
                self._play_sound(self.ohh_sound)
                self.game_over_screen()

    def _which_platform_hit(self, platform_hit_list):
        """Checks what kind of platform Joe has collided with. 
        The main_player's (Joe) friction value varies from which 
        kind of surface he is on"""

        for plat in platform_hit_list:
            if plat.snow:
                self.main_player.jump_power = PLAYER_JUMP - 2 #let him jump higher to make it fair when jumping over axes
                self.main_player.friction = -0.177 #Let Joe walk slower in the snow
                the_snow_spot = platform_hit_list[0].rect.top + platform_hit_list[0].get_size(False) // 2 #let Joe sink down in to the snow
            
                if self.main_player.position.y > platform_hit_list[0].rect.top:
                    if self.main_player.jumping:
                        self.main_player.velocity.y *= SNOW_GRAVITY #Let Joe drown in the snow slowly

                    self._adjust_player_platform_y_position(the_snow_spot) #Adjust Joe's y position until he reaches the_snow_spot
            elif plat.concrete:
                if not plat.transparent_plat: #transparent_plat=False then joe cant walk past the concrete platforms
                    if (self.main_player.rect.right >= plat.rect.left and len(platform_hit_list) > 2 or
                        self.main_player.rect.right >= plat.rect.left and self.main_player.jumping):
                        self.main_player.position.x -= 2
                    else:
                        self._adjust_player_platform_y_position(plat.rect.top)
            else: #The platform is a grass platform
                self.main_player.friction = -0.09   
                self._adjust_player_platform_y_position(plat.rect.top)

    def update(self):
        """Update function which updates every sprites,
        checks for a sprite collision and moves the camera.
        Put in helper functions later"""
      
        self.all_sprites.update()
        
        #Collision (rect collision) with the platform and stop the main_player if he hits the top of the plaform
        hits_platform = pygame.sprite.spritecollide(self.main_player, self.platforms, False) #List of platforms that Joe collided with
        if self.main_player.velocity.y > 0: #going down due to gravity
            if hits_platform:
                self._which_platform_hit(hits_platform)
                
        #blit the viewing perspective from Joe when he is reading on the sign (key input = (r))
        if self.display_bigger_sign:
            if self.run_once_sign:
                Sign(WIDTH / 2, HEIGHT * 3/4 - 10, 20, self)
                self.run_once_sign = False
        else:
            for sign in self.sign:
                if sign.type == "big":
                    sign.kill()

        #Sign collision
        sign_hit = pygame.sprite.spritecollide(self.main_player, self.sign, False)
        if sign_hit:
            if not self.display_bigger_sign:
                self.display_key_input_instructions = True
            else:
                self.display_key_input_instructions = False
        else:
            self.display_key_input_instructions = False

        #Game over scenarios
        #Fall off a platform
        if self.main_player.position.y - self.main_player.get_height() > HEIGHT:
            self.main_player.kill()
            self._game_over_functionality(self.scream_sound, "fell")

        #Don't let Joe go off the left side of the screen
        if self.main_player.position.x <= 0:
            self.main_player.position.x = 20

        #Function for traps collision, pass in hits_platform list which has a collsion 
        #detection between the player and the platforms
        """Uncomment this line below to enable traps collision with the player"""
        self.game_over_collision(hits_platform)

        self.move_main_player_camera() 
        self.change_level()
     
    def draw(self):
        """Redraw window function which blits text on 
        the window again and again"""

        WIN.fill(SKYBLUE)
        self.all_sprites.draw(WIN)
        #Display score and coins later

        if self.dead:
            self.play_again_btn = pygame.draw.rect(WIN, BUTTON_COLOR, (WIDTH / 2 - PLAY_BTN_WIDTH / 2, HEIGHT / 8 - 10, PLAY_BTN_WIDTH, PLAY_BTN_HEIGHT))
            self._draw_text(WIDTH / 2, HEIGHT / 7, "Deaths: {}".format(self.death_counter), 40, BLACK)
            self._draw_text(WIDTH / 2, 140, "Game Over!", 40, WHITE)
            self._draw_text(WIDTH / 2, 170, "Joe {}!".format(self.game_over_text), 40, WHITE)
            self._draw_text(WIDTH / 2, HEIGHT / 2, "Press \"Enter\" to play again!", 30, BLACK)

        if self.display_key_input_instructions:
            self._draw_text(self.pixel_sign.rect.centerx, self.pixel_sign.rect.y - 25, "Press r to read", 25, WHITE)
        if self.display_bigger_sign:
            line_space = 105 #Fix later (it is not good to hard code things)
            self._draw_text(WIDTH / 2, line_space, "Dear Joe. I was robbed by a red angry minotaur with big horns", 23, WHITE)
            self._draw_text(WIDTH / 2, line_space + 70, "Find him and get my valuable belongins back at any cost", 23, WHITE)
            self._draw_text(WIDTH / 2, line_space + 130, "The road is dangerous, watch out for traps", 23, WHITE)
            self._draw_text(WIDTH / 2, line_space + 200, "He will propably send enemies which can be hostile", 23, WHITE)
            self._draw_text(WIDTH / 2, line_space + 260, "Be cautious and use the greatest techniques to survive the wilderness", 23, WHITE)
            self._draw_text(WIDTH / 2, line_space + 320, "Sincerely yours, Jack", 23, WHITE)
            self._draw_text(WIDTH / 2, line_space + 360, "Press b to continue the adventure", 24, BLACK)

        pygame.display.flip()

    def run(self):
        """Game loop"""

        while self.playing:
            CLOCK.tick(FPS)
            self.events()
            self.update()
            self.draw()

    def opening_level_part1(self):
        """This function blits 1/2 (part1) of the opening level in the game"""

        self.main_player = MainCharacter(40, HEIGHT - 50, self)
        self.grass_platform = Platform(self.main_player.position.x - 40, BOTTOM_PLATFORM_Y_COORDINATE, self)
        self.pixel_sign = Sign(WIDTH * 3/4, BOTTOM_PLATFORM_Y_COORDINATE - 30, 2, self)
        GameTitle(WIDTH / 2, 100, self)

        for i in range(25):
            Platform(self.main_player.position.x + (self.grass_platform.get_size() * i), BOTTOM_PLATFORM_Y_COORDINATE, self)

    def test_level(self):
        """Function for designing levels (level 7)"""
        self.main_player = MainCharacter(40, HEIGHT - 50, self)
        self.grass_platform = Platform(self.main_player.position.x - 40, BOTTOM_PLATFORM_Y_COORDINATE, self)

        for i in range(8): #10
            if i == 4:
                bomb_plat = Platform(140 + (self.grass_platform.get_size() * i), 300, self, False, False, True) #Snow
            snow = Platform(140 + (self.grass_platform.get_size() * i), 300, self, False, False, True) #Snow


        for k in range(6):
            if k == 3:
                spawn_bomb_plat = Platform(snow.rect.x + 100 + (self.grass_platform.get_size() * k), HEIGHT / 2, self)
            Platform(snow.rect.x + 100 + (self.grass_platform.get_size() * k), HEIGHT / 2, self)

        Bomb(bomb_plat, self)
        Bomb(spawn_bomb_plat, self)

        
    def boss_level(self):
        pass

    def game_over_screen(self):
        self.main_player.velocity.x = 0

        if self.game_over_text != "fell":
            GraveStone(self.main_player.position.x - 100, self.main_player.position.y - 150, self)

        if self.run_once_death_counter:
            self.death_counter += 1
            self.run_once_death_counter = False

        for trap in self.traps:
            try:
                if not trap.spike: #kill every trap except the spike traps
                    trap.kill()
            except AttributeError: #It is an Attribute error because Bomb object does not have a spike attribute
                pass
            
        for fireball in self.fireballs:
            fireball.kill()

        self.main_player.kill()

def main(death_counter):
    obsticle_game = Game(death_counter)

    while obsticle_game.running:
        #obsticle_game.test_level()
        obsticle_game.opening_level_part1()
        obsticle_game.run()

main(0)