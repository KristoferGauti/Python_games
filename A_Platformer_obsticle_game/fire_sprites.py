import pygame
import random
from game_settings import *
from sprites import Platform

vector = pygame.math.Vector2

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
