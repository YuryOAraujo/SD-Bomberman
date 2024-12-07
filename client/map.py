import pygame
from spritesheet import SpriteSheet
from constants import *


class Map:
    def __init__(self, grid) -> None:
        self.grid = grid
        self.animations = self.load_animation_map()
        self.osbtacles = [[],[]]


    @staticmethod
    def load_animation_map() -> dict:
        sprite_sheet = SpriteSheet(pygame.image.load("client/graphics/bomb_party_v3.png").convert_alpha())

        animations = {
            "grass": sprite_sheet.get_image(1, 0, SPRITE_WIDTH, SPRITE_HEIGHT, SCALE, PINK),
            "box":  sprite_sheet.get_image(10, 5, SPRITE_WIDTH, SPRITE_HEIGHT, SCALE, PINK),
            "block": sprite_sheet.get_image(11, 4, SPRITE_WIDTH, SPRITE_HEIGHT, SCALE, PINK)
        }

        return animations

    def draw_map(self, screen) -> list:
        for row in range(len(self.grid)):
            for col in range(len(self.grid[row])):
                if self.grid[row][col] == 0:
                    screen.blit(self.animations["grass"], (col * SPRITE_WIDTH * SCALE, row * SPRITE_HEIGHT * SCALE))
                elif self.grid[row][col] == 1:
                    block_rect = pygame.Rect(col * SPRITE_WIDTH * SCALE, row * SPRITE_HEIGHT * SCALE, SPRITE_WIDTH * SCALE, SPRITE_HEIGHT * SCALE)
                    self.osbtacles[0].append(block_rect)
                    screen.blit(self.animations["block"], (col * SPRITE_WIDTH * SCALE, row * SPRITE_HEIGHT * SCALE))
                elif self.grid[row][col] == 2:
                    boxes_rect = pygame.Rect(col * SPRITE_WIDTH * SCALE, row * SPRITE_HEIGHT * SCALE, SPRITE_WIDTH * SCALE, SPRITE_HEIGHT * SCALE)
                    self.osbtacles[1].append(boxes_rect)
                    screen.blit(self.animations["box"], (col * SPRITE_WIDTH * SCALE, row * SPRITE_HEIGHT * SCALE))
        return self.osbtacles

