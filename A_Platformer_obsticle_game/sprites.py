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
        image = pygame.Surface((width, height)) #default background color is (0, 0, 0)
        image.fill(SPRITESHEET_BG_SURFACE_COLOR)

        image.blit(self.spritesheet, (0, 0), (x, y, width, height))
        if scale_up:
            image = pygame.transform.scale(image, (int(width * scale_num), int(height * scale_num)))
        else:
            image = pygame.transform.scale(image, (width // scale_num, height // scale_num))

        #Donnot fill the background color of the spritesheet surface black because set_colorkey((0, 0, 0))
        #will erase the black color from the sprite aswell as the background color 
        image.set_colorkey(SPRITESHEET_BG_SURFACE_COLOR) 

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
        self.friction = FRICTION
        self.jump_power = PLAYER_JUMP
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
        if not self.walking and not self.jumping:
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

        if self.walking:
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
            self.velocity.y += self.jump_power

    def cut_jump(self):
        mini_jump = self.jump_power // 4

        if self.jumping:
            if self.velocity.y < mini_jump:
                self.velocity.y = mini_jump

    def get_height(self):
        return self.image.get_height()

class Platform(pygame.sprite.Sprite):
    def __init__(self, x, y, game, grass=True, concrete=False, snow=False, transparent_plat=False):
        self._layer = PLATFORM_LAYER if not snow else SNOW_LAYER
        self.groups = game.all_sprites, game.platforms
        super().__init__(self.groups)
        self.game = game
        self.grass = grass
        self.concrete = concrete
        self.transparent_plat = transparent_plat #for the transparent castle where the boss_level starts
        self.snow = snow
        self.run_once = True
        self.concrete_plat_blown_up = False
        self.concrete_plat_qty = 0
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
        
    def update(self):
        concrete_platforms_qty_now = 0
        for plat in self.game.platforms:
            if plat.concrete:
                concrete_platforms_qty_now += 1

        if self.run_once:
            for plat in self.game.platforms:
                if plat.concrete:
                    self.concrete_plat_qty += 1
            self.run_once = False 

        if concrete_platforms_qty_now < self.concrete_plat_qty:
            self.concrete_plat_blown_up = True

class CastleDoorBackground(pygame.sprite.Sprite):
    """We need this background class to display the door's background because 
    the SpritesheetParser class takes the black background from all the sprites"""
    
    def __init__(self, x, y, game, door_open=True):
        self._layer = CASTLE_DOOR_LAYER - 1
        self.groups = game.all_sprites
        super().__init__(self.groups)
        black_surface = pygame.Surface((110, 100))
        black_surface.fill(BLACK)
        if door_open:
            self.image = black_surface
        else:
            self.image = game.castle_switch_cannon_sprite_sheet.get_image(399, 0, 73, 59, 2, 2)
        self.rect = self.image.get_rect()
        self.rect.center = (x, y + 10)

class CastleDoor(pygame.sprite.Sprite):
    def __init__(self, x, y, game):
        self._layer = CASTLE_DOOR_LAYER
        self.groups = game.all_sprites, game.door
        super().__init__(self.groups)
        self.game = game
        self.close_door = False
        self.last_update_time = 0
        self.current_frame_index = 0
        self._load_images()
        self.image = self.door_images_list[0]
        self.rect = self.image.get_rect()
        self.rect.midbottom = (x, y)

    def _load_images(self):
        self.door_images_list = [
            self.game.castle_switch_cannon_sprite_sheet.get_image(399, 0, 73, 59, 2, 2),
            self.game.castle_switch_cannon_sprite_sheet.get_image(399, 73, 67, 58, 2),
            self.game.castle_switch_cannon_sprite_sheet.get_image(150, 1840, 61, 61, 2),
            self.game.castle_switch_cannon_sprite_sheet.get_image(211, 1840, 59, 60, 2),
            self.game.castle_switch_cannon_sprite_sheet.get_image(399, 476, 72, 60, 2),
        ]
        self.reversed_door_images_list = self.door_images_list[::-1]

    def _animate(self, image_list):
        time_now = pygame.time.get_ticks()

        if time_now - self.last_update_time > 300:
            self.last_update_time = time_now
            self.current_frame_index = (self.current_frame_index + 1) % len(image_list)
            last_image_midbottom = self.rect.midbottom
            self.image = image_list[self.current_frame_index]
            self.rect = self.image.get_rect()
            self.rect.midbottom = last_image_midbottom
        
        CastleDoorBackground(self.rect.centerx, self.rect.centery, self.game) #Black square for the opened door background
        
        if self.current_frame_index == len(image_list) - 1:
            self.game.door_opened = True
            self.kill()

            if self.close_door:
                CastleDoorBackground(self.rect.centerx, self.rect.centery - 10, self.game, False) #closed door background image 
  
    def update(self):
        door_hit = pygame.sprite.spritecollide(self.game.main_player, self.game.door, False)

        if door_hit:
            self.game.door_collision = True
        else:
            self.game.door_collision = False

        if self.game.open_door:
            if not self.game.start_boss_level_list:
                self._animate(self.door_images_list)
        if self.close_door:              
            self._animate(self.reversed_door_images_list)

class DeathSwitch(pygame.sprite.Sprite):
    def __init__(self, spawn_wall_plat, game):
        self._layer = DEATH_SWITCH_LAYER
        self.groups = game.all_sprites, game.switcher 
        super().__init__(self.groups)
        self.game = game
        self.last_update_time = 0
        self.current_frame_index = 0
        self.switch_animate_up = False
        self.switch_is_on = False
        self._load_images()
        self.image = self.switch_img_list[0]
        self.rect = self.image.get_rect()
        self.rect.right = spawn_wall_plat.rect.left
        self.rect.y = spawn_wall_plat.rect.y
        self.mask = pygame.mask.from_surface(self.image)

    def _load_images(self):
        switch_img_list = [
            self.game.castle_switch_cannon_sprite_sheet.get_image(0, 0, 476, 399, 5, False),
            self.game.castle_switch_cannon_sprite_sheet.get_image(0, 952, 476, 399, 5, False),
            self.game.castle_switch_cannon_sprite_sheet.get_image(0, 476, 476, 399, 5, False)
        ]
        self.switch_img_list = [pygame.transform.rotate(img, 180) for img in switch_img_list]

    def _animate(self):
        time_now = pygame.time.get_ticks()

        if time_now - self.last_update_time > 400:
            self.last_update_time = time_now
            last_image_right = self.rect.right
            last_centery = self.rect.centery
            self.current_frame_index = (1 + self.current_frame_index) % len(self.switch_img_list)
            self.image = self.switch_img_list[self.current_frame_index]
            self.rect = self.image.get_rect()
            self.rect.right = last_image_right
            self.rect.centery = last_centery

        if self.current_frame_index == len(self.switch_img_list) - 1:
            self.image = self.switch_img_list[self.current_frame_index]
            self.switch_animate_up = False
            self.switch_is_on = True
            
    def update(self):
        switch_hit = pygame.sprite.spritecollide(self.game.main_player, self.game.switcher, False, pygame.sprite.collide_mask)
        if not self.switch_is_on:
            if switch_hit:
                self.switch_animate_up = True #run the animation
        else: #if the switch is on 
            for boss_death_plat in self.game.boss_platforms_list: #move all the platforms downwards to kill the minotaur
                boss_death_plat.kill()

        if self.switch_animate_up:
            self._animate()
