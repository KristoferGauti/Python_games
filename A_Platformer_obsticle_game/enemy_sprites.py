import pygame
import random
import os
import math
from game_settings import *
from boss_weapons import *

vector = pygame.math.Vector2

class MinotaurBoss(pygame.sprite.Sprite):
    def __init__(self, platform, game):
        self._layer = ENEMY_LAYER
        self.groups = game.all_sprites, game.enemies
        super().__init__(self.groups)
        self.game = game
        self.type = "boss"
        self.move = "stop"
        self.run_once = True
        self.move_left = True 
        self.shoot_fireball = True
        self.struck_a_lightning = True
        self.is_jumping = False
        self.current_frame_index = 0
        self.last_update_time = 0
        self.acceleration_x_speed = 1.3
        self.total_shot_firballs = 0
        self.fire_ball_qty_list = []
        self._load_images()
        self.image = self.standby_img_list[0]
        self.rect = self.image.get_rect()
        self.rect.bottom = platform.rect.top
        self.rect.centerx = platform.rect.centerx 
        self.position = vector(self.rect.centerx, self.rect.bottom)
        self.acceleration = vector(0, 0)
        self.velocity = vector(0, 0)
        self.mask = pygame.mask.from_surface(self.image)

    def _load_images(self):
        self.standby_img_list = [self.game.title_boss_sprite_sheet.get_image(769, 0, 64, 48, 3, True)]
        self.walking_left_img_list = [
            self.game.title_boss_sprite_sheet.get_image(817, 0, 64, 48, 3, True),
            self.game.title_boss_sprite_sheet.get_image(865, 0, 64, 48, 3, True),
            self.game.title_boss_sprite_sheet.get_image(913, 0, 64, 48, 3, True)
        ]
        self.walking_right_img_list = [pygame.transform.flip(img, True, False) for img in self.walking_left_img_list]

    def _animate(self):
        time_now = pygame.time.get_ticks()

        if time_now - self.last_update_time > 150:
            self.last_update_time = time_now
            last_image_bottom = self.rect.bottom
            if self.acceleration.x > 0:
                self.current_frame_index = (self.current_frame_index + 1) % len(self.walking_right_img_list)
                self.image = self.walking_right_img_list[self.current_frame_index]
            if self.acceleration.x < 0:
                self.current_frame_index = (self.current_frame_index + 1) % len(self.walking_left_img_list)
                self.image = self.walking_left_img_list[self.current_frame_index]
            if self.acceleration.x == 0:
                self.current_frame_index = (self.current_frame_index + 1) % len(self.standby_img_list)
                self.image = self.standby_img_list[self.current_frame_index]
            self.rect = self.image.get_rect()
            self.rect.bottom = last_image_bottom

    def _boss_moving_boundaries(self):
        """This function checks if the boss has dropped down dead and 
        it uses the moving boundaries function from the Game() object 
        to set moving boundaries for the minotaur boss"""

        if self.rect.top > HEIGHT:
            self.game.minotaur_is_dead = True
            self.kill()

        self.game._character_moving_boundaries(self)
        
        if self.rect.right > self.game.boss_platforms_list[-1].rect.right - 10:
            self.move = "left"

    def jump(self, jump_power):
        if not self.is_jumping:
            self.velocity.y += jump_power
            self.is_jumping = True

    def move_minotaur(self):
        self.acceleration = vector(0, MINOTAUR_GRAVITY)

        if self.move == "right":
            self.acceleration.x = self.acceleration_x_speed #walk right
        elif self.move == "left":
            self.acceleration.x = -self.acceleration_x_speed #walk left
        else:
            self.acceleration.x = 0

        self.velocity.y += self.acceleration.y
        self.position += self.velocity + self.acceleration
        self.rect.midbottom = self.position

    def _weapon_reset(self):
        self.shoot_fireball = True
        self.struck_a_lightning = True

    def minotaur_ai(self):
        if self.move_left:
            if self.position.x < self.game.main_player.position.x + 590: 
                self.move = "left"
                if self.position.x < self.game.main_player.position.x + 270: 
                    self.move = "stop" #The minotaur stops when he has reached 270 pixels radius from Joe
                    if random.randrange(1, 100) % 21 == 0: #4% chance of moving right
                        self.move_left = False
        else:
            self.move = "right"
            if random.randrange(1, 100) % 16 == 0: #6% chance of walking left
                self.move_left = True
                if random.randrange(1, 100) % 4 == 0: #25% chance of power jumping
                    self.jump(MINOTAUR_POWER_JUMP)

            else: #75% chance for reloading weapons
                self._weapon_reset()
 
        if self.move != "stop": #if the minotaur is moving then jump 
            if random.randrange(1, 100) % 50 == 0: #2% chance of small jumping
                self.jump(MINOTAUR_SMALL_JUMP)
        else:
            if random.randrange(1, 100) % 15 == 0: #6% chance of shooting a fireball
                if self.shoot_fireball:
                    random_margin = random.choice([10, 5, 2, 15, 12])
                    fire_ball = MinotaurFireBall(self.rect.left, self.rect.centery + random_margin, self.game)
                    self.fire_ball_qty_list.append(fire_ball)
                    self.shoot_fireball = False
                    self.total_shot_firballs += 1

                    if self.total_shot_firballs % 3 == 0: #Struck a lightning when total shots of fireballs is divisible by 3
                        if self.struck_a_lightning:
                            random_margin = random.choice([num for num in range(5, 31, 5)])
                            MinotaurLightning(random.randrange(self.game.boss_platforms_list[0].rect.centerx, self.rect.right - 40), HEIGHT / 5 - random_margin, self.game)
                            self.struck_a_lightning = False

    def update(self):
        self._animate()
        self._boss_moving_boundaries()
        self.move_minotaur()

        plat_hits = pygame.sprite.spritecollide(self, self.game.platforms, False)
        if plat_hits:
            self.velocity.y = 0
            self.position.y = plat_hits[0].rect.top
            self.is_jumping = False
            
        self.minotaur_ai()

        #This if statement allows only 2 fireballs to be on the screen at once
        if len(self.fire_ball_qty_list) > 2:
            self.fire_ball_qty_list[-1].kill()
            self.fire_ball_qty_list.clear()

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
        self.scale_down_num = 2 #if you change this number than you need to figure out the margin when the snake attacks
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
        If so the pop the second chosen 1 in self.random_num_list and append 2 so
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

        if self.fell_off_platforms:
            #Constant x velocity but changing y velocity due to gravity
            self.acceleration = vector(-self.acceleration_x_speed, GRAVITY)
        else:
            #check if the chopper has reached the initial_platform which is the end platform, if so change the direction
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
            for plat in platform_hit:
                if plat.concrete:
                    self.position.x, self.position.y = plat.rect.x, plat.rect.y
