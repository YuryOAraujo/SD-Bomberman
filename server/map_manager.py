from random import randint
from grid_base import *

SPRITE_WIDTH = 16
SPRITE_HEIGHT = 16
SCALE = 3

class MapManager:
    def __init__(self, stage_name):
        self.grid = GRID_BASE[stage_name]
        self.generate_boxes()

    def generate_boxes(self):

        """Gera caixas aleatoriamente no mapa."""
        for row in range(1, len(self.grid) - 1):
            for col in range(1, len(self.grid[row]) - 1):
                if self.grid[row][col] != 0:
                    continue
                elif (row < 3 or row > len(self.grid) - 4) and (col < 3 or col > len(self.grid[row]) - 4):
                    continue
                if randint(0, 9) < 7:
                    self.grid[row][col] = 2

    def destroy_boxes_around(self, position, radius=1):

        """Destrói as caixas ao redor de uma posição (apenas blocos destrutíveis, acima, abaixo, esquerda e direita)."""

        # Converte coordenadas de tela (pixels) para coordenadas de matriz (linhas e colunas)
        x = position[0] // (SPRITE_WIDTH * SCALE)  
        y = position[1] // (SPRITE_HEIGHT * SCALE) 

        # Direções: cima, baixo, esquerda, direita
        directions = [(-1, 0), (1, 0), (0, -1), (0, 1)]

        for dx, dy in directions:
            nx, ny = x + dx, y + dy

            if 0 <= ny < len(self.grid) and 0 <= nx < len(self.grid[ny]):
                if self.grid[ny][nx] == 2:  
                    self.grid[ny][nx] = 0  


    def get_grid(self):
        """Retorna o estado atual do mapa."""
        return self.grid