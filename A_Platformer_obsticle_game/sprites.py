import pygame
import random
import os
from time import sleep
from game_settings import *

vector = pygame.math.Vector2

class SpritesheetParser():
    def __init__(self, filename):
        self.spritesheet = pygame.image.load(filename).convert_alpha()

    def get_image(self, x, y, height, width, scale_num, scale_up=True):
        image = pygame.Surface((width, height))
        image.blit(self.spritesheet, (0, 0), (x, y, width, height))
        if scale_up:
            image = pygame.transform.scale(image, (int(width * scale_num), int(height * scale_num)))
        else:
            image = pygame.transform.scale(image, (width // scale_num, height // scale_num))
        image.set_colorkey(BLACK)

        return image

class MainCharacter(pygame.sprite.Sprite):
    def __init__(self, x, y, game):
        self._layer = MAIN_CHARACTER_LAYER
        self.groups = game.all_sprites
        super().__init__(self.groups)
        self.game = game
        self.walking = False
        self.jumping = False
        self.stand_left = False
        self.current_frame_index = 0
        self.last_update_time = 0
        self._load_images()
        self.image = self.standing_frames_right[0]
        self.rect = self.image.get_rect()
        self.position = vector(x, y)
        self.velocity = vector(0, 0)
        self.acceleration = vector(0, 0)
        self.friction = -0.09 
        self.mask = pygame.mask.from_surface(self.image)

    def _load_images(self):
        self.standing_frames_right = [self.game.main_sprite_sheet.get_image(17, 448, 34, 19, 2), self.game.main_sprite_sheet.get_image(36, 448, 34, 19, 2)]
        self.standing_frames_left = [pygame.transform.flip(frame, True, False) for frame in self.standing_frames_right] #transform.flip(image, flip_vertical, flip_horizontal)
        self.right_walking_frames = [self.game.main_sprite_sheet.get_image(55, 448, 33, 21, 2), 
                                     self.game.main_sprite_sheet.get_image(76, 448, 33, 21, 2), 
                                     self.game.main_sprite_sheet.get_image(97, 448, 33, 21, 2), 
                                     self.game.main_sprite_sheet.get_image(97, 448, 33, 21, 2), 
                                     self.game.main_sprite_sheet.get_image(118, 448, 33, 21, 2), 
                                     self.game.main_sprite_sheet.get_image(139, 448, 33, 21, 2), 
                                     self.game.main_sprite_sheet.get_image(160, 448, 33, 21, 2)]
        self.left_walking_frames = [pygame.transform.flip(frame, True, False) for frame in self.right_walking_frames]
        self.jumping_frames_right = [self.game.main_sprite_sheet.get_image(0, 448, 34, 17, 2), self.game.main_sprite_sheet.get_image(448, 384, 35, 20, 2)]
        self.jumping_frames_left = [pygame.transform.flip(frame, True, False) for frame in self.jumping_frames_right]

    def __change_jumping_frame(self, right_image, left_image):
        if not self.stand_left:
            self.image = right_image
        else:
            self.image = left_image

    def _animate(self):
        time_now = pygame.time.get_ticks()

        if int(self.velocity.x) != 0:
            self.walking = True
        else:
            self.walking = False

        #Standing animation
        if not self.walking and not self.jumping: #nearly the same code @@, put in a function later
            if time_now - self.last_update_time > 320:
                self.last_update_time = time_now
                self.current_frame_index = (self.current_frame_index + 1) % len(self.standing_frames_right)
                last_image_bottom = self.rect.bottom
                if self.stand_left:
                    self.image = self.standing_frames_left[self.current_frame_index]
                else:
                    self.image = self.standing_frames_right[self.current_frame_index]
                self.rect = self.image.get_rect()
                self.rect.bottom = last_image_bottom

        if self.walking: #nearly the same code @@
            if time_now - self.last_update_time > 90:
                self.last_update_time = time_now
                self.current_frame_index = (self.current_frame_index + 1) % len(self.left_walking_frames)
                last_image_bottom = self.rect.bottom
                if self.velocity.x > 0: #Player going to the right direction
                    self.image = self.right_walking_frames[self.current_frame_index]
                else:
                    self.image = self.left_walking_frames[self.current_frame_index]
                self.rect = self.image.get_rect()
                self.rect.bottom = last_image_bottom

        if int(self.velocity.y) < 0:
            self.__change_jumping_frame(self.jumping_frames_right[0], self.jumping_frames_left[0])
        elif int(self.velocity.y) > 0:
            self.__change_jumping_frame(self.jumping_frames_right[1], self.jumping_frames_left[1])
            
    def update(self):
        self._animate()

        self.acceleration = vector(0, GRAVITY)
        
        keys = pygame.key.get_pressed()
        if self.game.main_player_can_move:
            if keys[pygame.K_LEFT]:
                self.acceleration.x = -ACCELERATION
                self.stand_left = True
            if keys[pygame.K_RIGHT]:
                self.acceleration.x = ACCELERATION
                self.stand_left = False
        else:
            pass

        #Friction phisics equations
        self.acceleration.x += self.velocity.x * self.friction
        self.velocity += self.acceleration
        #Motion phisics equation
        self.position += self.velocity + (0.5 * self.acceleration)
        
        self.rect.midbottom = self.position

        
    def jump(self):
        self.rect.x += 10
        hits = pygame.sprite.spritecollide(self, self.game.platforms, False)
        self.rect.x -= 10
        if hits and not self.jumping:
            self.jumping = True
            self.velocity.y += PLAYER_JUMP

    def cut_jump(self):
        mini_jump = PLAYER_JUMP // 4

        if self.jumping:
            if self.velocity.y < mini_jump:
                self.velocity.y = mini_jump

    def get_height(self):
        return self.image.get_height()

class Platform(pygame.sprite.Sprite):
    def __init__(self, x, y, game, grass=True, concrete=False, snow=False):
        self._layer = PLATFORM_LAYER if not snow else SNOW_LAYER
        self.groups = game.all_sprites, game.platforms
        super().__init__(self.groups)
        self.game = game
        self.grass = grass
        self.concrete = concrete
        self.snow = snow
        if self.grass:
            self.image = self.game.main_sprite_sheet.get_image(128, 0, 128, 128, 3, False)
        elif self.concrete:
            self.image = self.game.main_sprite_sheet.get_image(0, 0, 128, 128, 3, False)
        elif self.snow:
            self.image = self.game.main_sprite_sheet.get_image(256, 0, 128, 128, 3, False)
        self.rect = self.image.get_rect()
        self.rect.x = x
        self.rect.y = y

    def get_size(self, width=True):
        if width:
            return self.image.get_width()
        else:
            return self.image.get_height()

class FireBall(pygame.sprite.Sprite):
    def __init__(self, x, y, game):
        self._layer = FIREBALL_LAYER
        self.groups = game.all_sprites, game.fireballs
        super().__init__(self.groups)
        self.game = game
        self.go_up = True
        self.random_time = random.choice([3000, 4000, 5000, 6000])
        self.last_update_time = 0
        self.last_update_time_lava_ball = 0
        self.current_frame_index = 0
        self._load_images()
        self.image = self.fireball_images_go_up[0]
        self.rect = self.image.get_rect()
        self.position = vector(x, y)
        self.velocity = vector(0, 0)
        self.acceleration = vector(0, 0)
        self.mask = pygame.mask.from_surface(self.image)

    def _load_images(self):
        images_list = [self.game.traps_sprite_sheet.get_image(260, 1970, 124, 220, 3, False),
                       self.game.traps_sprite_sheet.get_image(260, 2330, 124, 220, 3, False), 
                       self.game.traps_sprite_sheet.get_image(260, 2206, 124, 220, 3, False),
                       self.game.traps_sprite_sheet.get_image(260, 1846, 124, 220, 3, False),
                       self.game.traps_sprite_sheet.get_image(260, 2566, 124, 220, 3, False)]

        self.fireball_images_go_up = [pygame.transform.rotate(frame, 270) for frame in images_list]
        self.fireball_images_go_down = [pygame.transform.rotate(frame, 90) for frame in images_list]

    def _animate(self):
        time_now = pygame.time.get_ticks()

        if time_now - self.last_update_time > 100:
            self.last_update_time = time_now
            self.current_frame_index = (self.current_frame_index + 1) % len(self.fireball_images_go_up)
            if self.velocity.y < 0:
                self.image = self.fireball_images_go_up[self.current_frame_index]
            elif self.velocity.y > 0:
                self.image = self.fireball_images_go_down[self.current_frame_index]
        
    def update(self):
        self._animate()
        time_now = pygame.time.get_ticks()

        #calculate the upwards and downwards motion with respect to gravity and friction
        self.acceleration = vector(0, GRAVITY)
        self.acceleration.y += self.velocity.y * LAVA_BALL_FRICTION
        self.velocity += self.acceleration
        
        self.position += self.velocity + (0.5 * self.acceleration)
        self.rect.midtop = self.position #midtop is a tuple (x, y). Note: self.rect does not take a tuple with floats
        
        if self.go_up:
            self.velocity.y -= 45
            self.go_up = False

        #check if the lavaball goes into the lavapool, if so remove the lavaball sprite
        for lava in self.game.lavas:
            if lava.rect.y < self.position.y:
                self.position.y = lava.rect.centery
                if time_now - self.last_update_time_lava_ball > self.random_time: #let the fireball wait in the lava for 3, 4, 5 or 6 secs before going upwards again
                    self.last_update_time_lava_ball = time_now
                    self.velocity.y -= 18
                    self.go_up = True

class Lava(pygame.sprite.Sprite):
    def __init__(self, x, y, game, fireball=False):
        self._layer = LAVA_LAYER
        self.groups = game.all_sprites, game.lavas
        super().__init__(self.groups)
        self.game = game
        self.spawn_fireball = fireball
        self._load_images()
        self.last_update_time = 0
        self.current_frame_index = 0
        self.image = self.lava_bubbles_images[0]
        self.rect = self.image.get_rect()
        self.rect.x = x
        self.rect.y = y
        self.mask = pygame.mask.from_surface(self.image)

    def _load_images(self):
        self.lava_bubbles_images = [self.game.main_sprite_sheet.get_image(181, 448, 32, 32, 1.5),
                                    self.game.main_sprite_sheet.get_image(213, 448, 32, 32, 1.5),
                                    self.game.main_sprite_sheet.get_image(245, 448, 32, 32, 1.5)]

    def _animate(self):
        time_now = pygame.time.get_ticks()

        if time_now - self.last_update_time > 250:
            self.last_update_time = time_now
            self.current_frame_index = (self.current_frame_index + 1) % len(self.lava_bubbles_images)
            self.image = self.lava_bubbles_images[self.current_frame_index]

    def update(self):
        self._animate()
        if self.spawn_fireball:
            FireBall(self.rect.x, self.rect.y - self.get_height() - 20, self.game)
            self.spawn_fireball = False

    def get_height(self):
        return self.image.get_height()

"""Traps sprites in one class"""
class SingleFrameSpriteTrap(pygame.sprite.Sprite):
    def __init__(self, x, y, game, animation=True, spike=True, stone=False, axe=False):
        self._layer = TRAP_LAYER
        self.groups = game.all_sprites, game.traps
        super().__init__(self.groups)
        self.last_update_time = 0
        self.spike_update_time_2 = 0
        self.update_frame_index = 0
        self.game = game
        self.animation = animation
        self.spike = spike
        self.stone = stone
        self.axe = axe
        if self.spike:
            self.run_once = True
            self.spike_go_up = True
            self.spike_go_down = False 
            self.image = game.traps_sprite_sheet.get_image(260, 1486, 160, 164, 4, False)
        

        if self.stone or self.axe:
            self.axe_down = True
            the_image = game.traps_sprite_sheet.get_image(0, 0, 394, 394, 5, False) if self.stone else game.traps_sprite_sheet.get_image(0, 394, 372, 248, 5, False)
            self.stop_axe_image_list = [pygame.transform.rotate(the_image, angle) for angle in range(300, 360, 15)] #320
            self.random_num = random.randint(0, len(self.stop_axe_image_list) - 1)
            self.image_rotation_list = [pygame.transform.rotate(the_image, angle) for angle in range(0, 361, 90)]
            self.image = self.image_rotation_list[0]

        self.rect = self.image.get_rect()
        self.top = self.rect.top
        self.rect.x = x
        self.rect.y = y
        self.mask = pygame.mask.from_surface(self.image)
        self.starting_x_position = int(x)
        self.starting_y_position = int(y)

    def _animate(self):
        time_now = pygame.time.get_ticks()
        time_now_2 = pygame.time.get_ticks()

        if self.spike:
            #Spawn once a platform underneath the spike 
            if self.run_once:
                Platform(self.starting_x_position, self.starting_y_position, self.game) #grass platform
                self.run_once = False

            #Make the spikes go up and down 300, 200, 400, 100 ms per frame 
            if time_now - self.last_update_time > random.choice([300, 200, 400, 100]):
                self.last_update_time = time_now
                if self.spike_go_up:
                    self.rect.y -= 5
                if self.spike_go_down:
                    self.rect.y += 5
                if self.rect.y <= self.starting_y_position - SPIKE_HEIGHT:
                    self.spike_go_up = False
                    self.spike_go_down = True
                elif self.rect.y >= self.starting_y_position + 1: #when the spikes go behind the platform, hide the spikes behind the platform in 6 sec
                    self.rect.y -= 5
                    if time_now_2 - self.spike_update_time_2 > random.choice([4000, 3000, 5000]): #Hide behind the platform for 4, 3 or 5 sec
                        self.spike_update_time_2 = time_now_2
                        self.spike_go_up = True
                        self.spike_go_down = False
   
        if self.stone or self.axe:
            #Rotate the stone or axe image 90 degrees every 150 ms
            millisecs = 150 if self.stone else 70
            if time_now - self.last_update_time > millisecs:
                self.last_update_time = time_now
                self.update_frame_index = (self.update_frame_index + 1) % len(self.image_rotation_list)
                self.image = self.image_rotation_list[self.update_frame_index]

            self.rect.x -= 3

    def update(self):
        #check platform collsion
        hits = pygame.sprite.spritecollide(self, self.game.platforms, False)

        if self.animation:
            self._animate()
            
        if self.spike and not self.animation:
            #Display the platform beneath the spike
            if self.run_once:
                Platform(self.starting_x_position, self.starting_y_position + SPIKE_HEIGHT, self.game) #grass platform change x, y
                self.run_once = False

        if self.stone:
            self.rect.y += 2
            if hits:
                self.rect.y -= 2 #stop the ball's y position

            if self.rect.x + 100 <= 0:
                self.kill()
            
        if self.axe:
            self.rect.y += 3
            
            if hits:
                self.image = self.stop_axe_image_list[self.random_num]
                self.rect.x += 3
                self.rect.y -= 3

class Bomb(pygame.sprite.Sprite):
    def __init__(self, spawn_plat, game):
        self._layer = TRAP_LAYER
        self.groups = game.all_sprites, game.traps
        super().__init__(self.groups)
        self.game = game
        self.time_since_the_game_ran = 0
        self.run_once = True
        self.bomb_touched = False
        self.blow_the_bomb = False
        self.is_blowing = False
        self.last_update_time = 0
        self.current_frame_index = 0
        self.spawn_plat = spawn_plat
        self._load_blow_list_images()
        self.image = game.traps_sprite_sheet.get_image(260, 2454, 109, 151, 2, False) #y = 2094
        self.rect = self.image.get_rect()
        self.rect.centerx = self.spawn_plat.rect.centerx
        self.rect.bottom = self.spawn_plat.rect.top
        self.mask = pygame.mask.from_surface(self.image)

    def _load_blow_list_images(self):
        self.blow_list = [self.game.traps_sprite_sheet.get_image(0, 3626, 340, 388, 1, False),
                          self.game.traps_sprite_sheet.get_image(0, 3286, 340, 388, 1, False),
                          self.game.traps_sprite_sheet.get_image(0, 3966, 340, 388, 1, False), 
                          self.game.traps_sprite_sheet.get_image(0, 4646, 340, 388, 1, False),
                          self.game.traps_sprite_sheet.get_image(0, 4306, 340, 388, 1, False),
                          self.game.traps_sprite_sheet.get_image(0, 5326, 340, 388, 1, False),
                          self.game.traps_sprite_sheet.get_image(0, 4986, 340, 388, 1, False)]

    def mask_collision_using_overlap_and_offsets(self, obj1, obj2):
        """pixel perfect collision using pygame.mask"""
        
        offset_x = obj2.rect.x - obj1.rect.x
        offset_y = obj2.rect.y - obj1.rect.y

        return obj1.mask.overlap(self.mask, (offset_x, offset_y))


    def _bomb_trigger_wait(self):
        """This function starts counting 2 seconds when the 
        bomb trigger is on (red button sprite) and calls the animate 
        function to blow the bomb when 2 seconds have passed"""

        if self.run_once:
            self.time_since_the_game_ran = pygame.time.get_ticks()
            self.run_once = False
      
        if not self.blow_the_bomb and self.bomb_touched:
            self.image = self.game.traps_sprite_sheet.get_image(260, 2094, 109, 151, 2, False)

        if self.time_since_the_game_ran:
            time_since_touched_the_bomb = pygame.time.get_ticks() - self.time_since_the_game_ran #get the difference
            if time_since_touched_the_bomb > 2000: #if 1.4 or 1.6 or 1.7 seconds has passed since Joe has touched the bomb, then boom
                self.blow_the_bomb = True

    def _animate(self):
        self._bomb_trigger_wait()
        time_now = pygame.time.get_ticks()
        
        
        if self.blow_the_bomb:
            if time_now - self.last_update_time > 100:
                self.last_update_time = time_now

                last_image_bottom = self.rect.bottom
                last_centerx = self.rect.centerx
                self.current_frame_index = (self.current_frame_index + 1) % len(self.blow_list)
                self.image = self.blow_list[self.current_frame_index]
                self.mask = pygame.mask.from_surface(self.image)
                self.rect = self.image.get_rect()
                self.rect.bottom = last_image_bottom
                self.rect.centerx = last_centerx

            #Returns the offset coordinates (x, y) if Joe collides with the bomb otherwise None
            if self.mask_collision_using_overlap_and_offsets(self.game.main_player, self) != None:
                self.game._game_over_functionality(self.game.ohh_sound, "expoded to death")

        if self.current_frame_index == len(self.blow_list) - 1:
            self.kill()
            

    def update(self):
        if self.mask_collision_using_overlap_and_offsets(self.game.main_player, self) != None:
            self.bomb_touched = True
        
        if self.bomb_touched:
            self._animate()

       

            

"""Enemies sprites"""
class Snake(pygame.sprite.Sprite):
    def __init__(self, spawn_platform, game):
        self._layer = ENEMY_LAYER
        self.groups = game.all_sprites, game.enemies
        super().__init__(self.groups)
        self.game = game
        self.platform = spawn_platform
        self.type = "snake"
        self.random_num_list = []
        self.attack = False
        self.run_once = True
        self.random_num = 0
        self.last_update_time = 0
        self.last_update_time_attack = 0
        self.current_frame_index = 0
        self.scale_down_num = 2
        self._load_images()
        self.image = self.snake_list[0]
        self.rect = self.image.get_rect()
        self.rect.centerx = self.platform.rect.centerx
        self.rect.bottom = self.platform.rect.top
        self.mask = pygame.mask.from_surface(self.image)

    def _load_images(self):
        self.snake_list = [self.game.traps_sprite_sheet.get_image(276, 5666, 224, 188, self.scale_down_num, False),
                           self.game.traps_sprite_sheet.get_image(276, 5926, 224, 188, self.scale_down_num, False),
                           self.game.traps_sprite_sheet.get_image(276, 6186, 224, 188, self.scale_down_num, False),
                           self.game.traps_sprite_sheet.get_image(276, 6446, 224, 188, self.scale_down_num, False),
                           self.game.traps_sprite_sheet.get_image(260, 766, 224, 188, self.scale_down_num, False),
                           self.game.traps_sprite_sheet.get_image(260, 1126, 224, 188, self.scale_down_num, False)]

        self.attack_list = [self.game.traps_sprite_sheet.get_image(0, 5666, 260, 276, self.scale_down_num, False), 
                            self.game.traps_sprite_sheet.get_image(0, 6446, 260, 276, self.scale_down_num, False),
                            self.game.traps_sprite_sheet.get_image(0, 5926, 260, 276, self.scale_down_num, False),
                            self.game.traps_sprite_sheet.get_image(0, 6186, 260, 276, self.scale_down_num, False)]

    def _check_if_random_chooses_one_twice_in_a_row(self):
        """This algorithm checks if self.random_num chooses 1 twice in a row 
        If so the pop the second 1 in self.random_num_list and append 2 so
        that the snake does not bite twice in a row (the snake bites when self.random_num = 1)"""

        if len(self.random_num_list) > 1:
            for index, number in enumerate(self.random_num_list):
                if number == 1:
                    if number == self.random_num_list[index - 1]:
                        the_right_random_num = 2
                        self.random_num_list.pop()
                        self.random_num_list.append(the_right_random_num)
                if number == 2:
                    if number == self.random_num_list[index - 1] and number == self.random_num_list[index - 2]:
                        the_right_random_num = 1
                        self.random_num_list.pop()
                        self.random_num_list.append(the_right_random_num)

    def _animate(self):
        time_now = pygame.time.get_ticks()
    
        if time_now - self.last_update_time > 500:
            self.last_update_time = time_now
            old_centerx = self.rect.centerx
            old_centery = self.rect.centery
            if not self.attack:
                self.current_frame_index = (self.current_frame_index + 1) % len(self.snake_list)
                self.image = self.snake_list[self.current_frame_index]

                if not self.run_once:
                    self.rect.centerx = old_centerx + 50 #x and y margin for the sprite because the attack frames width and
                    self.rect.centery = old_centery + 18 #height are not the same as the width and the height on the standing snake frames
                    self.run_once = True
            else:
                self.current_frame_index = (self.current_frame_index + 1) % len(self.attack_list)
                self.image = self.attack_list[self.current_frame_index]

                if self.run_once:
                    self.rect.centerx = old_centerx - 50
                    self.rect.centery = old_centery - 18
                    self.run_once = False
        
    def update(self):
        random_attack_time_now = pygame.time.get_ticks()

        if random_attack_time_now - self.last_update_time_attack > 2000: #Wait for 2 seconds
            self.last_update_time_attack = random_attack_time_now
            self.random_num = random.randint(1, 3) #25% chance that the snake attacks
            self.random_num_list.append(self.random_num)

            self._check_if_random_chooses_one_twice_in_a_row()

            if self.random_num_list[len(self.random_num_list) - 1] > 1: 
                self.attack = False
            else: #if the last number in self.random_num_list = 1
                self.attack = True #Then attack once
                self.run_once = True
        
        self._animate()

class SwordChopper(pygame.sprite.Sprite):
    def __init__(self, platform, platform_length, scale_up_num, game, fell_off_platforms=True, speed=2.1):
        self._layer = ENEMY_LAYER
        self.groups = game.all_sprites, game.enemies
        super().__init__(self.groups)
        self.game = game
        self.scale_up_num = scale_up_num
        self.spawn_plat = platform
        self.type = "sword chopper"
        self.length_of_platforms = platform_length
        self.fell_off_platforms = fell_off_platforms
        self.acceleration_x_speed = speed
        self.last_update_time = 0
        self.current_frame_index = 0
        self._load_images()
        self.image = self.img_list_left[0]
        self.rect = self.image.get_rect()
        self.rect.bottom = self.spawn_plat.rect.top 
        self.rect.centerx = self.spawn_plat.rect.centerx
        self.initial_x_position = self.rect.centerx
        self.position = vector(self.rect.centerx, self.rect.bottom)
        self.acceleration = vector(0, 0)
        self.velocity = vector(0, 0)
        self.mask = pygame.mask.from_surface(self.image)

    def _load_images(self):
        self.img_list_right = [self.game.main_sprite_sheet.get_image(384, 320, 64, 64, self.scale_up_num),
                               self.game.main_sprite_sheet.get_image(448, 320, 64, 64, self.scale_up_num),
                               self.game.main_sprite_sheet.get_image(0, 320, 64, 64, self.scale_up_num),
                               self.game.main_sprite_sheet.get_image(384, 320, 64, 64, self.scale_up_num),
                               self.game.main_sprite_sheet.get_image(64, 320, 64, 64, self.scale_up_num),
                               self.game.main_sprite_sheet.get_image(128, 320, 64, 64, self.scale_up_num),
                               self.game.main_sprite_sheet.get_image(320, 320, 64, 64, self.scale_up_num),
                               self.game.main_sprite_sheet.get_image(192, 320, 64, 64, self.scale_up_num),
                               self.game.main_sprite_sheet.get_image(256, 320, 64, 64, self.scale_up_num)]

        self.img_list_left = [pygame.transform.flip(frame, True, False) for frame in self.img_list_right]
            

    def _animate(self):
        time_now = pygame.time.get_ticks()

        if time_now - self.last_update_time > 500:
            self.last_update_time = time_now
            self.current_frame_index = (self.current_frame_index + 1) % len(self.img_list_left)
            last_image_bottom = self.rect.bottom
            if self.acceleration.x > 0:
                self.image = self.img_list_right[self.current_frame_index]
            else:
                self.image = self.img_list_left[self.current_frame_index]
            self.rect = self.image.get_rect()
            self.rect.bottom = last_image_bottom


    def update(self):
        self._animate()
        #print(self.acceleration)

        if self.fell_off_platforms:
            #Constant x velocity but changing y velocity due to gravity
            self.acceleration = vector(-self.acceleration_x_speed, GRAVITY)
        else:
            if self.position.x <= self.initial_x_position - self.length_of_platforms:
                self.acceleration = vector(self.acceleration_x_speed, GRAVITY)
            elif self.position.x >= self.initial_x_position:
                self.acceleration = vector(-self.acceleration_x_speed, GRAVITY)
            

        self.velocity.y += self.acceleration.y
        self.position += self.velocity + self.acceleration
        self.rect.midbottom = self.position


        platform_hit = pygame.sprite.spritecollide(self, self.game.platforms, False, pygame.sprite.collide_mask)
        if platform_hit:
            self.position.y = platform_hit[0].rect.top
            self.velocity.y = 0
            







        

"""One frame sprites"""
class GameTitle(pygame.sprite.Sprite):
    def __init__(self, x, y, game):
        self._layer = TITLE_LAYER
        self.groups = game.all_sprites
        super().__init__(self.groups)
        self.game = game
        self.image = game.title_boss_sprite_sheet.get_image(0, 0, 75, 769, 1)
        self.rect = self.image.get_rect()
        self.rect.centerx = x
        self.rect.centery = y
        self.initial_player_x_pos = game.main_player.position.x

    def update(self):
        if int(self.game.main_player.position.x) > self.initial_player_x_pos + 160:
            self.rect.centerx -= 5

class Sign(pygame.sprite.Sprite):
    def __init__(self, x, y, scale_num, game):
        self._layer = PIXEL_SIGN_LAYER
        self.groups = game.all_sprites, game.sign
        super().__init__(self.groups)
        self.scale_num = scale_num
        self.type = "small" if self.scale_num < 5 else "big" 
        self.image = game.title_boss_sprite_sheet.get_image(961, 0, 42, 30, scale_num)
        self.rect = self.image.get_rect()
        self.rect.centerx = x
        self.rect.centery = y

class GraveStone(pygame.sprite.Sprite):
    def __init__(self, x, y, game):
        self._layer = MAIN_CHARACTER_LAYER
        self.groups = game.all_sprites
        super().__init__(self.groups)
        self.game = game
        self.image = game.traps_sprite_sheet.get_image(388, 3458, 100, 100, 2)
        self.rect = self.image.get_rect()
        self.rect.x = x
        self.rect.y = y


        