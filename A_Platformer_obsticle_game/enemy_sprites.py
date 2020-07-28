import pygame
import random
from game_settings import *
from sprites import Platform

vector = pygame.math.Vector2

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
