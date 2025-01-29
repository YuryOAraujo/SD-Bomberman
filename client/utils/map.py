import pygame
from utils.spritesheet import SpriteSheet
from config.constants import *

class Map:

    """
    Classe que representa o mapa do jogo.

    Gerencia a renderização do mapa, carregamento de sprites, e detecção de 
    obstáculos com base em um grid.
    """

    def __init__(self, grid, stage_name) -> None:

        """
        Inicializa a classe `Map` com o grid e configurações iniciais.

        Args:
            grid (list): Matriz que representa o layout do mapa, onde cada célula 
                        contém um valor indicando o tipo de terreno ou obstáculo.
                        Valores possíveis:

                        - 0: Chão (livre de obstáculos)
                        - 1: Bloco indestrutível
                        - 2: Caixa destrutível
            stage_name (str): Nome do estágio do mapa (e.g., "Stage 1", "Stage 2").
        """

        self.grid = grid
        self.stage_name = stage_name
        self.animations = self.load_animation_map(self)
        self.obstacles = [[], []]
        self.static_map_surface = pygame.Surface((WIDTH, HEIGHT))
        self.draw_static_map()

    @staticmethod
    def load_animation_map(self) -> dict:

        """
        Carrega os sprites necessários para o mapa a partir de uma spritesheet.

        Returns:
            dict: Dicionário contendo os sprites de cada elemento do mapa, onde as 
                chaves são os nomes dos elementos (e.g., "floor", "box", "block") e 
                os valores são as superfícies correspondentes.
        """

        sprite_sheet = SpriteSheet(pygame.image.load(PATH_SPRITES).convert_alpha())

        stage_mapping = {
            "Stage 1": {"floor": 1, "box": 10},
            "Stage 2": {"floor": 4, "box": 9},
        }

        stage_data = stage_mapping[self.stage_name]

        animations = {
            "floor": sprite_sheet.get_image(stage_data['floor'], 0, SPRITE_WIDTH, SPRITE_HEIGHT, SCALE, PINK),
            "box": sprite_sheet.get_image(stage_data['box'], 5, SPRITE_WIDTH, SPRITE_HEIGHT, SCALE, PINK),
            "block": sprite_sheet.get_image(11, 4, SPRITE_WIDTH, SPRITE_HEIGHT, SCALE, PINK)
        }

        return animations

    def update_obstacles(self):

        """
        Atualiza a lista de obstáculos com base no grid atual.

        Os obstáculos são separados em duas categorias:
            - Blocos indestrutíveis (armazenados em `self.obstacles[0]`)
            - Caixas destrutíveis (armazenadas em `self.obstacles[1]`)

        Essa lista é usada para detecção de colisões no jogo.
        """

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
        
        """
        Desenha a superfície estática do mapa baseada no grid inicial.

        Para cada célula no grid:
            - Grama (0): Adiciona o sprite de grama à superfície.
            - Bloco indestrutível (1): Adiciona o sprite de bloco e registra o 
            obstáculo.
            - Caixa destrutível (2): Adiciona o sprite de caixa e registra o 
            obstáculo.

        Ao final, atualiza a lista de obstáculos chamando `update_obstacles`.
        """

        for row in range(len(self.grid)):
            for col in range(len(self.grid[row])):
                x = col * SPRITE_WIDTH * SCALE
                y = row * SPRITE_HEIGHT * SCALE

                if self.grid[row][col] == 0:
                    self.static_map_surface.blit(self.animations["floor"], (x, y))
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
        """
        Renderiza o mapa na tela com base na superfície estática gerada.

        Args:
            screen (pygame.Surface): Superfície principal onde o mapa será desenhado.
            offset_x (int, optional): Deslocamento horizontal do mapa. Útil para 
                                    efeitos como scrolling. Padrão é 0.

        Returns:
            list: Lista de obstáculos atualizada, onde:
                - `obstacles[0]` contém os retângulos de blocos indestrutíveis.
                - `obstacles[1]` contém os retângulos de caixas destrutíveis.
        """
        screen.blit(self.static_map_surface, (offset_x, 0))
        return self.obstacles