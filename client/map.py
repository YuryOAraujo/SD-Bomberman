import pygame
from spritesheet import SpriteSheet
from constants import *

class Map:

    def __init__(self, grid) -> None:
        self.grid = grid
        self.animations = self.load_animation_map()
        self.obstacles = [[], []]
        self.static_map_surface = pygame.Surface((WIDTH, HEIGHT))
        self.draw_static_map()

    @staticmethod
    def load_animation_map() -> dict:
        sprite_sheet = SpriteSheet(pygame.image.load("client/graphics/bomb_party_v3.png").convert_alpha())

        animations = {
            "grass": sprite_sheet.get_image(1, 0, SPRITE_WIDTH, SPRITE_HEIGHT, SCALE, PINK),
            "box": sprite_sheet.get_image(10, 5, SPRITE_WIDTH, SPRITE_HEIGHT, SCALE, PINK),
            "block": sprite_sheet.get_image(11, 4, SPRITE_WIDTH, SPRITE_HEIGHT, SCALE, PINK)
        }

        return animations

    def update_obstacles(self):

        """Atualiza a lista de obstáculos com base no grid atual."""
        self.obstacles = [[], []]  # Limpa a lista de obstáculos

        for row in range(len(self.grid)):
            for col in range(len(self.grid[row])):
                x = col * SPRITE_WIDTH * SCALE
                y = row * SPRITE_HEIGHT * SCALE

                if self.grid[row][col] == 1:  # Bloco indestrutível
                    block_rect = pygame.Rect(x, y, SPRITE_WIDTH * SCALE, SPRITE_HEIGHT * SCALE)
                    self.obstacles[0].append(block_rect)
                elif self.grid[row][col] == 2:  # Caixa destrutível
                    boxes_rect = pygame.Rect(x, y, SPRITE_WIDTH * SCALE, SPRITE_HEIGHT * SCALE)
                    self.obstacles[1].append(boxes_rect)
        
    def draw_static_map(self):

        for row in range(len(self.grid)):
            for col in range(len(self.grid[row])):
                x = col * SPRITE_WIDTH * SCALE
                y = row * SPRITE_HEIGHT * SCALE

                if self.grid[row][col] == 0:
                    self.static_map_surface.blit(self.animations["grass"], (x, y))
                elif self.grid[row][col] == 1:
                    block_rect = pygame.Rect(x, y, SPRITE_WIDTH * SCALE, SPRITE_HEIGHT * SCALE)
                    self.obstacles[0].append(block_rect)
                    self.static_map_surface.blit(self.animations["block"], (x, y))
                elif self.grid[row][col] == 2:
                    boxes_rect = pygame.Rect(x, y, SPRITE_WIDTH * SCALE, SPRITE_HEIGHT * SCALE)
                    self.obstacles[1].append(boxes_rect)
                    self.static_map_surface.blit(self.animations["box"], (x, y))
        
        # Atualiza a lista de obstáculos
        self.update_obstacles()

    def draw_map(self, screen, offset_x=0):
        screen.blit(self.static_map_surface, (offset_x, 0))
        return self.obstacles