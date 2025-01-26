import pygame
from spritesheet import SpriteSheet
from constants import *


class Map:
    def __init__(self, grid) -> None:
        self.grid = grid
        self.animations = self.load_animation_map()
        self.osbtacles = [[], []]

    @staticmethod
    def load_animation_map() -> dict:
        sprite_sheet = SpriteSheet(pygame.image.load("client/graphics/bomb_party_v3.png").convert_alpha())

        animations = {
            "grass": sprite_sheet.get_image(1, 0, SPRITE_WIDTH, SPRITE_HEIGHT, SCALE, PINK),
            "box": sprite_sheet.get_image(10, 5, SPRITE_WIDTH, SPRITE_HEIGHT, SCALE, PINK),
            "block": sprite_sheet.get_image(11, 4, SPRITE_WIDTH, SPRITE_HEIGHT, SCALE, PINK)
        }

        return animations

    def draw_map(self, screen, offset_x=0) -> list:
        """
        Desenha o mapa na tela.

        :param screen: Superfície do Pygame onde o mapa será desenhado.
        :param offset_x: Deslocamento horizontal (não será usado aqui).
        :return: Lista de obstáculos.
        """
        for row in range(len(self.grid)):
            for col in range(len(self.grid[row])):
                # Aplica o deslocamento horizontal (offset_x) às coordenadas x
                x = col * SPRITE_WIDTH * SCALE
                y = row * SPRITE_HEIGHT * SCALE

                if self.grid[row][col] == 0:
                    screen.blit(self.animations["grass"], (x, y))
                elif self.grid[row][col] == 1:
                    block_rect = pygame.Rect(x, y, SPRITE_WIDTH * SCALE, SPRITE_HEIGHT * SCALE)
                    self.osbtacles[0].append(block_rect)
                    screen.blit(self.animations["block"], (x, y))
                elif self.grid[row][col] == 2:
                    boxes_rect = pygame.Rect(x, y, SPRITE_WIDTH * SCALE, SPRITE_HEIGHT * SCALE)
                    self.osbtacles[1].append(boxes_rect)
                    screen.blit(self.animations["box"], (x, y))
        return self.osbtacles