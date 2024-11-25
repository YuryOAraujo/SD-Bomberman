import pygame
from constants import *
from spritesheet import SpriteSheet

class Player(pygame.sprite.Sprite):
    def __init__(self, player_id: int):
        super().__init__()
        self.player_id = player_id
        self.animations = self.load_animations()
        self.direction = "down"
        self.image = self.animations[self.direction][0]
        self.rect = self.image.get_rect()
        self.rect.center = (400, 300)
        self.speed = 5
        self.frame_index = 1
        self.animation_speed = 0.15
        self.moving = False

    def player_input(self):
        keys = pygame.key.get_pressed()
        self.moving = False
        if keys[pygame.K_LEFT] or keys[pygame.K_a] and self.rect.left > 0:
            self.rect.x -= self.speed
            self.direction = "left"
            self.moving = True
        elif keys[pygame.K_RIGHT] or keys[pygame.K_d] and self.rect.right < WIDTH:
            self.rect.x += self.speed
            self.direction = "right"
            self.moving = True
        elif keys[pygame.K_UP] or keys[pygame.K_w] and self.rect.top > 0:
            self.rect.y -= self.speed
            self.direction = "up"
            self.moving = True
        elif keys[pygame.K_DOWN] or keys[pygame.K_s] and self.rect.bottom < HEIGHT:
            self.rect.y += self.speed
            self.direction = "down"
            self.moving = True

    def update_animation(self):
        if self.moving:
            self.frame_index += self.animation_speed
            if self.frame_index >= len(self.animations[self.direction]):
                self.frame_index = 1
            self.image = self.animations[self.direction][int(self.frame_index)]
        else:
            self.image = self.animations[self.direction][0]

    def set_position(self, new_position):
        if self.rect.topleft != new_position:
            self.moving = True
        else:
            self.moving = False
        self.rect.topleft = new_position

    def load_animations(self):
        sprite_sheet = SpriteSheet(pygame.image.load("client/graphics/bomb_party_v3.png").convert_alpha())

        animations = {
            "down": [],
            "up": [],
            "left": [],
            "right": []
        }

        images = []

        for num in range (PLAYER_ANIMATION_LENGTH):
            images.append(sprite_sheet.get_image(num, self.player_id, SPRITE_WIDTH, SPRITE_HEIGHT, SCALE, PINK))

        animations["down"] = images[1:4]
        animations["up"] = [images[0], images[8], images[9]]
        animations["right"] = images[4:8]
        animations["left"] = [pygame.transform.flip(image, True, False).convert_alpha() for image in images[4:8]]

        return animations

    def update(self, is_local_player=False):
        if is_local_player:
            self.player_input()
        self.update_animation()
