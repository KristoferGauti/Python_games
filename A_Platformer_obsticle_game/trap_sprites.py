import pygame
import random
from game_settings import *
from sprites import Platform


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
        self.run_once = True
        if self.spike:
            self.spike_go_up = True
            self.spike_go_down = False 
            self.image = game.traps_sprite_sheet.get_image(260, 1486, 160, 164, 4, False)
        

        if self.stone or self.axe:
            self.axe_down = True
            the_image = game.traps_sprite_sheet.get_image(0, 0, 394, 394, 5, False) if self.stone else game.traps_sprite_sheet.get_image(0, 394, 372, 248, 5, False)
            self.stop_axe_image_list = [pygame.transform.rotate(the_image, angle) for angle in range(300, 360, 15)] 
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
                if self.run_once:
                    self.game.boulder_roll_sound.play()
                    self.run_once = False
                self.rect.y -= 2 #stop the ball's y position
            else:
                self.game.boulder_roll_sound.stop()

            if self.rect.x + 100 <= 0:
                self.kill()
            
        if self.axe:
            self.rect.y += 3

            if hits:
                self.rect.y -= 3
                self.rect.x += 3
                if hits[0].snow:
                    if self.run_once:
                        self.rect.y += hits[0].get_size(False) // 2
                        self.game.axe_hit_sound.play()
                        self.run_once = False
                else:
                    if self.run_once:
                        self.game.axe_hit_sound.play()
                        self.run_once = False
                
                self.image = self.stop_axe_image_list[self.random_num]

class CannonHead(pygame.sprite.Sprite):
    def __init__(self, x, y, game):
        self._layer = CANNON_LAYER
        self.groups = game.all_sprites
        super().__init__(self.groups)
        cannon_head_image = game.castle_switch_cannon_sprite_sheet.get_image(0, 1840, 67, 150, 1)
        self.image = pygame.transform.rotate(cannon_head_image, 150)
        self.rect = self.image.get_rect()
        self.rect.centerx = x
        self.rect.centery = y

class CannonBullet(pygame.sprite.Sprite):
    def __init__(self, x, y, bullet_type, game):
        self._layer = TRAP_LAYER
        self.groups = game.all_sprites, game.cannon_bullets
        super().__init__(self.groups)
        self.bullet_type = bullet_type
        self.last_update_time = 0
        self.update_frame_index = 0
        if self.bullet_type == "stone":
            the_image = game.traps_sprite_sheet.get_image(0, 0, 394, 394, 5, False)
        elif self.bullet_type == "axe":
            the_image = game.traps_sprite_sheet.get_image(0, 394, 372, 248, 5, False)
        self.image_rotation_list = [pygame.transform.rotate(the_image, angle) for angle in range(0, 361, 90)]
        self.image = self.image_rotation_list[0]
        self.rect = self.image.get_rect()
        self.rect.x = x
        self.rect.y = y

    def _animate(self):
        time_now = pygame.time.get_ticks()

        millisecs = 150 if self.bullet_type == "stone" else 70
        if time_now - self.last_update_time > millisecs:
            self.last_update_time = time_now
            self.update_frame_index = (self.update_frame_index + 1) % len(self.image_rotation_list)
            self.image = self.image_rotation_list[self.update_frame_index]

    def update(self):
        self._animate()

        self.rect.x -= random.randrange(5, 10)
        self.rect.y -= random.randrange(3, 5)

class Cannon(pygame.sprite.Sprite):
    def __init__(self, spawn_platform, game):
        self._layer = CANNON_LAYER + 1
        self.groups = game.all_sprites
        super().__init__(self.groups)
        self.game = game
        self.last_update_time = 0
        self.random_num = 0
        self.image = self.game.castle_switch_cannon_sprite_sheet.get_image(399, 952, 68, 86, 1) #Cannon stand
        self.rect = self.image.get_rect()
        self.rect.centerx = spawn_platform.rect.centerx
        self.rect.bottom = spawn_platform.rect.top
        self.cannon_head = CannonHead(self.rect.x - 5, self.rect.y - 5, self.game)
        self.bullet = CannonBullet(self.cannon_head.rect.x - 40, self.cannon_head.rect.y - 20, "axe", self.game)

    def update(self):
        """The cannon shoots either a stone or an axe.
        There is a 34% chance of shooting an axe 66% chance of shooting a stone"""

        if self.bullet.rect.bottom < 0 or self.bullet.rect.right < 0:
            time_now = pygame.time.get_ticks()
            if time_now - self.last_update_time > 2000: #2 seconds cooldown
                self.last_update_time = time_now
                self.random_num = random.randrange(1,100)

                if not self.game.dead:
                    if self.random_num % 3 == 0: #34% chance
                        self.bullet.kill()
                        self.bullet = CannonBullet(self.cannon_head.rect.x - 40, self.cannon_head.rect.y - 20, "axe", self.game)
                    else: #66% chance
                        self.bullet.kill()
                        self.bullet = CannonBullet(self.cannon_head.rect.x - 40, self.cannon_head.rect.y - 20, "stone", self.game)
            
                self.game.touched_an_object_play_sound = True
                self.game._play_object_sound(self.game.cannon_boom_sound)

class Bomb(pygame.sprite.Sprite):
    def __init__(self, spawn_plat, game, scale_down_explosion_sprites_num=1):
        self._layer = TRAP_LAYER
        self.groups = game.all_sprites, game.traps
        super().__init__(self.groups)
        self.game = game
        self.time_since_the_game_ran = 0
        self.run_once = True
        self.bomb_touched = False
        self.blow_the_bomb = False
        self.is_blowing = False
        self.scale_down_num = scale_down_explosion_sprites_num
        self.last_update_time = 0
        self.current_frame_index = 0
        self.spawn_plat = spawn_plat
        self._load_blow_list_images()
        self.image = game.traps_sprite_sheet.get_image(260, 2454, 109, 151, 2, False) #y = 2094
        self.rect = self.image.get_rect()
        self.rect.centerx = self.spawn_plat.rect.centerx
        self.rect.bottom = self.spawn_plat.rect.top if self.spawn_plat.grass or self.spawn_plat.concrete else self.spawn_plat.rect.centery
        self.mask = pygame.mask.from_surface(self.image)

    def _load_blow_list_images(self):
        self.blow_list = [self.game.traps_sprite_sheet.get_image(0, 3626, 340, 388, self.scale_down_num, False),
                          self.game.traps_sprite_sheet.get_image(0, 3286, 340, 388, self.scale_down_num, False),
                          self.game.traps_sprite_sheet.get_image(0, 3966, 340, 388, self.scale_down_num, False), 
                          self.game.traps_sprite_sheet.get_image(0, 4646, 340, 388, self.scale_down_num, False),
                          self.game.traps_sprite_sheet.get_image(0, 4306, 340, 388, self.scale_down_num, False),
                          self.game.traps_sprite_sheet.get_image(0, 5326, 340, 388, self.scale_down_num, False),
                          self.game.traps_sprite_sheet.get_image(0, 4986, 340, 388, self.scale_down_num, False)]

    def mask_collision_using_overlap_and_offsets(self, obj1, obj2):
        """pixel perfect collision using pygame.mask better explaining later"""
        
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
        """Animates the bomb's explosion"""
        self._bomb_trigger_wait()
        time_now = pygame.time.get_ticks()
        
        
        if self.blow_the_bomb:
            if time_now - self.last_update_time > 100:
                self.last_update_time = time_now

                last_image_bottom = self.rect.bottom
                last_centerx = self.rect.centerx
                self.current_frame_index = (self.current_frame_index + 1) % len(self.blow_list)
                self.image = self.blow_list[self.current_frame_index]
                self.mask = pygame.mask.from_surface(self.image) #new mask
                self.rect = self.image.get_rect()
                self.rect.bottom = last_image_bottom
                self.rect.centerx = last_centerx

            #Returns the offset coordinates (x, y) if Joe collides with the bomb otherwise None
            if self.mask_collision_using_overlap_and_offsets(self.game.main_player, self) != None:
                if not self.game.dead: #So the game_over_text does not change when Joe is already dead
                    self.game._game_over_functionality(self.game.ohh_sound, "exploded to death")

        if self.current_frame_index == len(self.blow_list) - 1: #remove the bomb object from game.all_sprites when done exploding
            self.game.touched_an_object_play_sound = True
            self.game._play_object_sound(self.game.bomb_boom_sound)
            self.kill()
            
    def update(self):
        if self.mask_collision_using_overlap_and_offsets(self.game.main_player, self) != None:
            self.bomb_touched = True

        if self.bomb_touched:
            self._animate()
            
        plat_hits = pygame.sprite.spritecollide(self, self.game.platforms, False, pygame.sprite.collide_mask)
        for plat in plat_hits:
            if plat.concrete:
                plat.kill()
