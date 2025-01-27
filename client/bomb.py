import pygame
import time
from constants import *
from spritesheet import SpriteSheet

class Bomb(pygame.sprite.Sprite):
    def __init__(self, x, y, player_id, player=None, timer=1):
        super().__init__()
        self.player_id = player_id
        self.player = player
        self.x = x
        self.y = y
        self.timer = timer
        self.explosion_range = player.explosion_range
        self.planted = time.time()
        self.animations = self.load_bomb_asset()
        self.animation_speed = 0.15
        self.frame_index = 0
        self.image = self.animations["bomb"][0]
        self.rect = self.image.get_rect(topleft=(x, y))
        self.exploding = False
        self.explosion_sprites = {}
        self.explosion_alpha = 0
        self.flicker_speed = 10
        self.flicker_timer = 0

    def load_bomb_asset(self) -> dict:
        sprite_sheet = SpriteSheet(pygame.image.load("client/graphics/bomb_party_v3.png").convert_alpha())

        animations = {
            "bomb": [sprite_sheet.get_image(12, 2, SPRITE_WIDTH, SPRITE_HEIGHT, SCALE, PINK),
                     sprite_sheet.get_image(12, 3, SPRITE_WIDTH, SPRITE_HEIGHT, SCALE, PINK),
                     sprite_sheet.get_image(12, 4, SPRITE_WIDTH, SPRITE_HEIGHT, SCALE, PINK)],
            "explosion_fade": [sprite_sheet.get_image(2, 5, SPRITE_WIDTH, SPRITE_HEIGHT, SCALE, PINK),
                               sprite_sheet.get_image(15, 5, SPRITE_WIDTH, SPRITE_HEIGHT, SCALE, PINK),
                               sprite_sheet.get_image(15, 4, SPRITE_WIDTH, SPRITE_HEIGHT, SCALE, PINK),
                               sprite_sheet.get_image(15, 3, SPRITE_WIDTH, SPRITE_HEIGHT, SCALE, PINK)],
            "explosion_path": [sprite_sheet.get_image(0, 5, SPRITE_WIDTH, SPRITE_HEIGHT, SCALE, PINK),
                               sprite_sheet.get_image(1, 5, SPRITE_WIDTH, SPRITE_HEIGHT, SCALE, PINK),
                               sprite_sheet.get_image(3, 5, SPRITE_WIDTH, SPRITE_HEIGHT, SCALE, PINK),
                               sprite_sheet.get_image(15, 0, SPRITE_WIDTH, SPRITE_HEIGHT, SCALE, PINK),
                               sprite_sheet.get_image(15, 1, SPRITE_WIDTH, SPRITE_HEIGHT, SCALE, PINK),
                               sprite_sheet.get_image(15, 2, SPRITE_WIDTH, SPRITE_HEIGHT, SCALE, PINK)],
        }

        return animations

    def should_explode(self) -> bool:
        return time.time() - self.planted >= self.timer

    def calculate_explosion_path(self):
        directions = {
            "left": (-1, 0),
            "right": (1, 0),
            "up": (0, -1),
            "down": (0, 1),
        }
        explosion_tiles = [((self.rect.x, self.rect.y), "center")]

        for direction, (dx, dy) in directions.items():
            for step in range(1, self.explosion_range + 1):
                x = self.rect.x + dx * (SPRITE_WIDTH * SCALE) * step
                y = self.rect.y + dy * (SPRITE_HEIGHT * SCALE) * step

                if not self.valid_tile(x, y):
                    break

                if step == self.explosion_range:
                    explosion_tiles.append(((x, y), direction))
                else:
                    explosion_tiles.append(((x, y), "path"))

        return explosion_tiles

    def valid_tile(self, x, y):
        return 0 <= x < PLAYABLE_AREA and 0 <= y < PLAYABLE_AREA

    def explode(self):
        self.exploding = True
        self.frame_index = 1

        explosion_tiles = self.calculate_explosion_path()
        self.explosion_sprites = {}

        for (x, y), direction in explosion_tiles:
            if direction == "center":
                sprite = self.animations["explosion_fade"][0].copy()
            elif direction == "left":
                sprite = self.animations["explosion_path"][0].copy()
            elif direction == "right":
                sprite = self.animations["explosion_path"][2].copy()
            elif direction == "up":
                sprite = self.animations["explosion_path"][3].copy()
            elif direction == "down":
                sprite = self.animations["explosion_path"][5].copy()
            else:
                if x != self.rect.x:
                    sprite = self.animations["explosion_path"][1].copy()
                elif y != self.rect.y:
                    sprite = self.animations["explosion_path"][4].copy()

            sprite.set_alpha(0)
            self.explosion_sprites[(x, y)] = sprite

    def update(self, surface):
        if not self.exploding:
            self.frame_index += self.animation_speed
            if self.frame_index >= len(self.animations["bomb"]):
                self.frame_index = 0

            self.image = self.animations["bomb"][int(self.frame_index)]

            if self.should_explode():
                self.image = self.animations["explosion_fade"][0]
                self.explode()
        else:
            self.flicker_timer += 1
            if self.flicker_timer >= self.flicker_speed:
                self.flicker_timer = 0
                self.explosion_alpha = 0 if self.explosion_alpha == 255 else 255

            self.image.set_alpha(self.explosion_alpha)
            surface.blit(self.image, self.rect.topleft)

            for (x, y), sprite in self.explosion_sprites.items():
                sprite.set_alpha(self.explosion_alpha)
                surface.blit(sprite, (x, y))

            if time.time() - self.planted >= self.timer + 1:  
                self.player.bombs_placed -= 1
                self.kill()