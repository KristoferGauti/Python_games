import pygame
from game_settings import *

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
        self.image = game.traps_sprite_sheet.get_image(388, 3458, 100, 100, 2)
        self.rect = self.image.get_rect()
        self.rect.x = x
        self.rect.y = y

class GoldPile(pygame.sprite.Sprite):
    def __init__(self, spawn_plat, game):
        self._layer = GOLD_PILE_LAYER
        self.groups = game.all_sprites
        super().__init__(self.groups)
        self.image = game.castle_switch_cannon_sprite_sheet.get_image(0, 1428, 412, 472, 3, False)
        self.rect = self.image.get_rect()
        self.rect.centerx = spawn_plat.rect.centerx
        self.rect.bottom = spawn_plat.rect.top + 10


