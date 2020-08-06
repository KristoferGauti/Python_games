"""Author: Kristofer Gauti"""
"""Adventurous Joe is an obsticle game which was inspired by Super Mario"""

"""Enemy sprites are from https://szadiart.itch.io/animated-character-pack?download"""
"""Main character is from https://jesse-m.itch.io/jungle-pack"""
"""The traps are from https://opengameart.org/content/animated-traps-and-obstacles"""

"""TODO: Camera system - Done
         code snow levels - Done
         Implement a death counter - Done
         code a castle enterance with the cannon and axe cannon - Done
         in the castle is the boss level (minotour level) - Done
         code backgrounds and visuals (snow falling down in the snow level and more) - Done
         code winning screen - Done
         code highscore functionality with a .txt file - Done
         code in more sounds
"""

import pygame
import random
import os
from time import sleep

from game_settings import *
from sprites import *
from levels import *
from one_frame_sprites import *

class Game():
    """To debug the castle levels set self.level_index = 12 
    and self.start_boss_level_list = True otherwise
    self.level_index = 12 and self.start_boss_level_list = False"""
    def __init__(self, death_counter):
        self.running = True
        self.playing = True
        self.run_once_sign = True
        self.run_once_death_counter = True
        self.reset_variables_once = True
        self.run_boss_opening_lvl_once = True
        self.main_player_can_move = True
        self.draw_level = True
        self.blit_forest_background = True
        self.blit_castle_background = True
        self.reset_camera = False
        self.dead = False
        self.game_over = False
        self.display_key_input_instructions = False
        self.display_bigger_sign = False
        self.stop_camera_movement = False
        self.door_collision = False 
        self.open_door = False
        self.door_opened = False
        self.minotaur_is_dead = False
        self.start_boss_level_list = False
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
        self.cannon_bullets = pygame.sprite.Group()
        self.enemies = pygame.sprite.Group() 
        self.sign = pygame.sprite.Group()
        self.door = pygame.sprite.Group()
        self.switcher = pygame.sprite.Group()
        self.boss_weapons = pygame.sprite.Group()
        self._load_data()
        self.level_index = 0 
        self.death_counter = death_counter
        self.levels_list = [opening_level_part2, level_1, level_2, level_3, level_4, level_5, level_6, level_7, initial_snow_level, level_9, last_snow_level, level_11, castle_level]
        self.boss_level_list = [boss_level] #castle levels
        self.boss_platforms_list = []
        self.snow_coordinates_list = [[random.randrange(0, WIDTH), random.randrange(-HEIGHT, 0)] for _ in range(200)] #200 snowflakes
  
    def _load_data(self):
        self.main_sprite_sheet = SpritesheetParser(os.path.join(self.spritesheet_dir, "enemies_maincharacter_spritesheet.png"))
        self.traps_sprite_sheet = SpritesheetParser(os.path.join(self.spritesheet_dir, "traps_rip_joe_spritesheet.png"))
        self.title_boss_sprite_sheet = SpritesheetParser(os.path.join(self.spritesheet_dir, "title_sign_boss_spritesheet.png"))
        self.castle_switch_cannon_sprite_sheet = SpritesheetParser(os.path.join(self.spritesheet_dir, "castle_final_level_spritesheet.png" ))
        self.visuals_sprite_sheet = SpritesheetParser(os.path.join(self.spritesheet_dir, "visuals_spritesheet.png"))

        #Load the highscore
        with open(os.path.join(self.__dirname, "highscore.txt"), "r") as file:
            try:
                self.highscore = int(file.read())
            except:
                self.highscore = 1000 #1000 deaths is the initial highscore

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

                if self.door_collision:
                    if event.key == pygame.K_o:
                        self.open_door = True
                        self.main_player_can_move = False
                        
                if self.dead:
                    if event.key == pygame.K_RETURN:
                        main(self.death_counter)

            if self.main_player_can_move:
                if event.type == pygame.KEYUP:
                    self.main_player.cut_jump()

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
                        self.game_over_text = "was stung to death!"
                        return True
                    if (trap_hit_list[0].spike_go_down and trap_hit_list[0].rect.bottom or
                    trap_hit_list[0].spike_go_down and trap_hit_list[0].rect.left or
                    trap_hit_list[0].spike_go_down and trap_hit_list[0].rect.right):
                        return False

                except IndexError:
                    self.game_over_text = "was stung to death!"
                    return True
                
            elif trap_hit_list[0].stone:
                self.game_over_text = "was hit by a boulder and died!"
                return True

            elif trap_hit_list[0].axe:
                self.game_over_text = "was cut by an axe to death!"
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
                if enemy.type == "sword chopper" :
                    enemy.position.x -= camera_speed
                    enemy.initial_x_position -= camera_speed
                    if enemy.position.x + 50 < 0 or enemy.position.y > HEIGHT + 50:
                        enemy.kill()
                elif enemy.type == "boss":
                    enemy.position.x -= camera_speed

            self.main_player.position.x -= camera_speed 

    def change_level(self, level_list):
        """If the camera's x coordinate has reached the 
        width of the screen - 50 then blit the next level 
        and reset the camera to its initial x coordinate"""

        if self.camera_movement_x_coordinate == WIDTH - 50:
            #print("Next level!")
            self.main_player.position.x += 5
            self.level_index += 1
            self.reset_camera = True
            self.draw_level = True

        #This function blits the upcomming next levels
        if self.draw_level: #draw the level once
            try:
                level_list[self.level_index](self.grass_platform, self) #self.levels_list is a list containing functions of the levels in levels.py
            except IndexError:
                self.stop_camera_movement = True

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
                self.game_over_text = "got eaten by snakes!"
                return True
            if enemy.type == "sword chopper":
                self.game_over_text = "was chopped to death!"
                return True
            if enemy.type == "boss":
                self.game_over_text = "was killed by the red angry minotaur"
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
        bullet_hit = pygame.sprite.spritecollide(self.main_player, self.cannon_bullets, False, pygame.sprite.collide_mask)
        boss_weapon_hit = pygame.sprite.spritecollide(self.main_player, self.boss_weapons, False, pygame.sprite.collide_mask)

        if lava_hits:
            self._game_over_functionality([self.ohh_sound, self.burning_sound], "was burned to death!")
        if fireball_hits:
            self._game_over_functionality([self.ohh_sound, self.burning_sound], "was fireballed to death!")
        if trap_hit:
            if self._check_trap_hit(trap_hit, hits_platform):
                self.dead = True
                self._play_sound(self.ohh_sound)
                self.game_over_screen()
        if bullet_hit:
            if bullet_hit[0].bullet_type == "stone":
                self._game_over_functionality(self.ohh_sound, "was hit by a boulder and died!")
            else:
                self._game_over_functionality(self.ohh_sound, "was cut by an axe to death!")
        if boss_weapon_hit:
            if not self.game_over: #run once boolean
                if boss_weapon_hit[0].type == "fireball":
                    self._game_over_functionality(self.ohh_sound, "was burned to death!")
                if boss_weapon_hit[0].type == "lightning":
                    self._game_over_functionality(self.ohh_sound, "was struck by a lightning to death!")
                self.game_over = True
                
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
                self.main_player.friction = -0.15 #Let Joe walk slower in the snow
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
            else: #The platform is a grass platform or castle platform
                self.main_player.friction = -0.09   
                self._adjust_player_platform_y_position(plat.rect.top)

    def _castle_door_functionality(self):
        """Function that animates the open and closing 
        animation for the castle door in the castle_level"""

        #run the self.boss_level_list
        if self.start_boss_level_list:
            self.main_player_can_move = True
            if self.run_boss_opening_lvl_once:
                self.opening_boss_level()
                self.run_boss_opening_lvl_once = False

        if self.door_opened: #when the door animation is done then...
            if not self.start_boss_level_list: #if this if statement does not exist then the platforms disappear
                for sprite in self.all_sprites: #remove all the sprites except for the main_player, Joe
                    if sprite._layer != MAIN_CHARACTER_LAYER:
                        sprite.kill()

            #reset the variables which are necessary for the boss_level_list
            if self.reset_variables_once: 
                self.level_index = -1 #self.opening_boss_level() is the level at -1 index
                self.camera_movement_x_coordinate = CAMERA_FOCUSPOINT_X_POS
                self.start_boss_level_list = True
                self.stop_camera_movement = False
                self.reset_variables_once = False

            self.door_opened = False
        else:
            #close the door
            if self.start_boss_level_list:
                self.castle_door.close_door = True

    def _character_moving_boundaries(self, character):
        """This function sets the characters moving boundaries so
        that the character does not go out of the screen"""

        if character.position.x <= 0:
            character.position.x = 20
        elif character.position.x >= WIDTH and self.stop_camera_movement:
            character.position.x = WIDTH - 20

    def _blit_background(self, background_img_obj, list_of_levels):
        for x in range(len(list_of_levels) + 2): #+2 because the len(boss_level_list) = 1 and the opening boss level are two levels
            background_img_obj(WIDTH * x, 0, self)
            
    def update(self):
        """Update function which updates every sprites,
        checks for a sprite collision and moves the camera"""
      
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

        #Fall off a platform
        if self.main_player.position.y - self.main_player.get_height() > HEIGHT:
            self.main_player.kill()
            self._game_over_functionality(self.scream_sound, "fell")

        #Don't let Joe go off the left or right side of the screen
        self._character_moving_boundaries(self.main_player)
        
        """Uncomment this line below to enable traps collision with the player"""
        #self.game_over_collision(hits_platform)

        #Blit levels functionality
        if not self.stop_camera_movement: #when the main_player's camera is moving
            self.move_main_player_camera() 

            if not self.start_boss_level_list:
                if self.blit_forest_background:
                    self._blit_background(ForestBackground, self.levels_list) #Blit the forest background
                    self.blit_forest_background = False

                self.change_level(self.levels_list)
            else:
                if self.blit_castle_background:
                    self._blit_background(CastleBackground, self.boss_level_list) #Blit the castle background
                    self.blit_castle_background = False

                self.change_level(self.boss_level_list)

        #This function executes when the castle door in the castle level opens
        self._castle_door_functionality()
        
    def draw(self):
        """Redraw window function which blits text on 
        the window again and again"""

        WIN.fill(SKYBLUE)
        self.all_sprites.draw(WIN)
        #Display score and coins later

        if self.dead:
            WIN.fill(DEATHBGCOLOR)
            self.all_sprites.draw(WIN)
            self._draw_text(WIDTH / 2, HEIGHT / 7, "Deaths: {}".format(self.death_counter), 40, WHITE)
            self._draw_text(WIDTH / 2, 140, "Game Over!", 40, WHITE)
            self._draw_text(WIDTH / 2, 170, "Joe {}!".format(self.game_over_text), 40, WHITE)
            self._draw_text(WIDTH / 2, HEIGHT / 2, "Press \"Enter\" to play again!", 30, WHITE)

        if self.display_key_input_instructions: #for the small sign
            self._draw_text(self.pixel_sign.rect.centerx, self.pixel_sign.rect.y - 25, "Press r to read", 25, WHITE)

        if self.display_bigger_sign: #display text for the bigger sign
            line_space = 105
            self._draw_text(WIDTH / 2, line_space, "Dear Joe. I was robbed by a red angry minotaur with big horns", 25, WHITE)
            self._draw_text(WIDTH / 2, line_space + 70, "Find him and get my precious pile of gold back at any cost", 25, WHITE)
            self._draw_text(WIDTH / 2, line_space + 130, "The road is dangerous, watch out for traps", 25, WHITE)
            self._draw_text(WIDTH / 2, line_space + 200, "He will propably send enemies which can be hostile", 25, WHITE)
            self._draw_text(WIDTH / 2, line_space + 260, "Be cautious and use the greatest techniques to survive the wilderness", 25, WHITE)
            self._draw_text(WIDTH / 2, line_space + 320, "Sincerely yours, Jack", 25, WHITE)
            self._draw_text(WIDTH / 2, line_space + 360, "Press b to continue the adventure", 26, WHITE)

        if not self.start_boss_level_list:
            if self.door_collision and not self.open_door:
                self._draw_text(castle_level.door.rect.centerx, castle_level.door.rect.y - 20, "Press o to open the door", 25, WHITE)    

        #Make it snow in the snow levels
        if not self.start_boss_level_list:
            if self.level_index >= 8:
                for coordinate in self.snow_coordinates_list:
                    pygame.draw.circle(WIN, WHITE, coordinate, 3)
                    coordinate[1] += 2

                    if not self.level_index >= 12:
                        if coordinate[1] > HEIGHT:
                            new_x_pos = random.randrange(0, WIDTH)
                            new_y_pos = random.randrange(-50, -10)
                            coordinate[0], coordinate[1] = new_x_pos, new_y_pos

        
        #Display the winner text
        if self.minotaur_is_dead:
            self.main_player_can_move = False
            
            #Save the new highscore if the old one was broken
            if self.death_counter <= self.highscore:
                self.highscore = self.death_counter
                self._draw_text(WIDTH / 2, 50, "NEW HIGH SCORE!!!", 40, WHITE)
                
                with open(os.path.join(self.__dirname, "highscore.txt"), "w") as file:
                    file.write(str(self.death_counter))

            self._draw_text(WIDTH / 2, HEIGHT / 2 - 75, "Congratulation. You won the game!", 40, WHITE)
            self._draw_text(WIDTH / 2, HEIGHT / 2 - 50, "The Highscore: {} deaths".format(self.highscore), 40, WHITE)
            self._draw_text(WIDTH / 2, HEIGHT / 2, "Your score: {} deaths".format(self.death_counter), 40, WHITE)

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
        self.pixel_sign = Sign(WIDTH / 5 + 80, BOTTOM_PLATFORM_Y_COORDINATE - 30, 2, self)
        GameTitle(WIDTH / 2, 100, self)

        for i in range(25):
            plat = Platform(self.main_player.position.x + (self.grass_platform.get_size() * i), BOTTOM_PLATFORM_Y_COORDINATE, self)
            if i in [9, 10]:
                SingleFrameSpriteTrap(plat.rect.x, plat.rect.y - SPIKE_NO_ANIMATION_HEIGHT_MARGIN, self, False) #spike no animation
            if i in [x for x in range(17, 21)]:
                SingleFrameSpriteTrap(plat.rect.x, plat.rect.y, self)

    def opening_boss_level(self):
        self.main_player.position.x, self.main_player.position.y = 150, HEIGHT - 50
        self.castle_door = CastleDoor(self.main_player.position.x + 30, self.main_player.position.y + 10, self)
        door_torch = Torch(self.castle_door.rect.right - 20, self.castle_door.rect.y - self.castle_door.image.get_height() // 4, self)
        Torch(self.castle_door.rect.left - 90, self.castle_door.rect.y - self.castle_door.image.get_height() // 4, self)
        self.grass_platform = Platform(0, BOTTOM_PLATFORM_Y_COORDINATE, self)

        for i in range(1, 47):
            if i < 20:
                if i % 5 == 0:
                    Torch(95 * i, door_torch.rect.y, self)
            if i == 38:
                Platform(self.grass_platform.rect.x + (self.grass_platform.get_size() * i), BOTTOM_PLATFORM_Y_COORDINATE - self.grass_platform.get_size() // 2, self) #one step up platform
            elif i >= 39:
                """The boss platforms"""
                boss_death_plat = Platform(self.grass_platform.rect.x + (self.grass_platform.get_size() * i), BOTTOM_PLATFORM_Y_COORDINATE - self.grass_platform.get_size(), self)
                self.boss_platforms_list.append(boss_death_plat)
            else:
                Platform(self.grass_platform.rect.x + (self.grass_platform.get_size() * i), BOTTOM_PLATFORM_Y_COORDINATE, self) #bottom platforms y = HEIGHT - 50
        
    def game_over_screen(self):
        self.main_player.velocity.x = 0

        if self.run_once_death_counter:
            self.death_counter += 1
            if self.game_over_text != "fell":
                GraveStone(self.main_player.position.x - 100, self.main_player.position.y - 150, self)

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
        obsticle_game.opening_level_part1()
        obsticle_game.run()

main(0)