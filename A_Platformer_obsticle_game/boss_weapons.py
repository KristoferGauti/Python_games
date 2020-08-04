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

class MinotaurLightning(pygame.sprite.Sprite):
    def __init__(self, x, y, game):
        self._layer = FIREBALL_LAYER
        self.groups = game.all_sprites, game.boss_weapons
        super().__init__(self.groups)
        self.type = "lightning"
        self.game = game
        self.last_update_time = 0
        self.current_frame_index = 0
        self._load_images()
        self.image = self.lightning_struck_img_list[0]
        self.rect = self.image.get_rect()
        self.rect.x = x
        self.rect.y = y

    def _load_images(self):
        scale_num = 1
        self.lightning_struck_img_list = [
            self.game.traps_sprite_sheet.get_image(0, 766, 360, 260, scale_num),
            self.game.traps_sprite_sheet.get_image(248, 394, 360, 260, scale_num),
            self.game.traps_sprite_sheet.get_image(0, 1126, 360, 260, scale_num),
            self.game.traps_sprite_sheet.get_image(0, 2206, 360, 260, scale_num),
            self.game.traps_sprite_sheet.get_image(0, 2926, 360, 260, scale_num),
            self.game.traps_sprite_sheet.get_image(0, 2566, 360, 260, scale_num),
            self.game.traps_sprite_sheet.get_image(0, 1486, 360, 260, scale_num),
            self.game.traps_sprite_sheet.get_image(0, 1846, 360, 260, scale_num)
        ]

    def _animate(self):
        time_now = pygame.time.get_ticks()

        if time_now - self.last_update_time > 400:
            self.last_update_time = time_now
            self.current_frame_index = (1 + self.current_frame_index) % len(self.lightning_struck_img_list)
            self.image = self.lightning_struck_img_list[self.current_frame_index]
        
        if self.current_frame_index == len(self.lightning_struck_img_list) - 1:
            self.kill()

    def update(self):
        self._animate()


        

