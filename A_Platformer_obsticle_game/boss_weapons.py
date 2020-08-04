import pygame
from game_settings import *
from fire_sprites import FireBall


class MinotaurFireBall(FireBall):
    def __init__(self, x, y, game):
        self._layer = FIREBALL_LAYER
        self.groups = game.all_sprites, game.boss_weapons
        pygame.sprite.Sprite.__init__(self, self.groups) #Fireball has already pygame.sprite.Sprite
        self.game = game
        self.type = "fireball"
        self.last_update_time = 0
        self.current_frame_index = 0
        FireBall._load_images(self)
        self.image = self.fireball_img_list[0]
        self.rect = self.image.get_rect()
        self.rect.x = x
        self.rect.y = y 
        
    def _animate(self):
        time_now = pygame.time.get_ticks()

        if time_now - self.last_update_time > 300:
            self.last_update_time = time_now
            self.current_frame_index = (1 + self.current_frame_index) % len(self.fireball_img_list)
            self.image = self.fireball_img_list[self.current_frame_index]

    def update(self):
        self._animate()

        self.rect.x -= 1.5
        
        #Check boundaries
        if self.rect.right < 0:
            self.kill()

        

