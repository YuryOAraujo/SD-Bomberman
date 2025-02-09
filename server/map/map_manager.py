from random import randint
from .grid_base import *
import copy

from config.constants import *
from random import choice, randint

class MapManager:

    def __init__(self, stage_name):

        self.stage_name = stage_name

        # Faz uma cópia profunda do grid base para não modificar a base original
        self.grid = self.grid = copy.deepcopy(GRID_BASE[stage_name])

        self.initial_grid = None

        # 3: flame, 4: bomb 5: speed
        self.powers = [3, 4, 5]  

        # Quantidade de cada poder (exemplo: 3 chama, 3 bomba, 4 velocidade)
        self.power_count = {3: 3, 4: 3, 5: 4}  

        # Armazena as posições dos poderes
        self.power_positions = []  

        self.power_probabilities = self.calculate_power_probabilities()

        # Número de poderes
        self.num_powers = 10  

        # Distância mínima entre os poderes
        self.min_distance = 3  

        self.generate_boxes()
        self.generate_power_positions()

    def calculate_power_probabilities(self):

        """Calcula as probabilidades de cada poder com base na quantidade desejada."""

        total_count = sum(self.power_count.values())
        probabilities = {power: count / total_count for power, count in self.power_count.items()}
        return probabilities

    def generate_power_positions(self):

        """Gera as posições para os poderes, mas não coloca no mapa ainda."""

        while len(self.power_positions) < self.num_powers:

            # Gera uma posição aleatória para um poder

            row = randint(1, len(self.grid) - 2)
            col = randint(1, len(self.grid[row]) - 2)

            # Verifica se a posição é válida (caixa) e se está suficientemente distante das outras
            if self.grid[row][col] == 2 and self.is_far_enough((row, col)):
                self.power_positions.append((row, col))
    
    def is_far_enough(self, new_position):

        """Verifica se a nova posição está suficientemente distante das posições dos poderes existentes."""

        for pos in self.power_positions:

            """
            Calcula a entre as posições 
            [usa a formula  distância Manhattan, também conhecida como distância de táxi ou distância L1, 
            é uma medida de distância entre dois pontos em um grid]
            """

            if abs(pos[0] - new_position[0]) < self.min_distance and abs(pos[1] - new_position[1]) < self.min_distance:
                return False
            
        return True

    def place_power(self, position):

        """Coloca um poder aleatório na posição fornecida."""

        power = choice(self.powers)
        self.grid[position[0]][position[1]] = power
        print("colocou o poder: ", power)

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
        
        self.initial_grid = copy.deepcopy(self.grid)

    def destroy_boxes_around(self, position, radius=1):

        """Destrói as caixas ao redor de uma posição (apenas blocos destrutíveis, acima, abaixo, esquerda e direita)."""

        x = position[0] // (SPRITE_WIDTH * SCALE)  
        y = position[1] // (SPRITE_HEIGHT * SCALE) 

        directions = [(-1, 0), (1, 0), (0, -1), (0, 1)]

        for dx, dy in directions:

            nx, ny = x + dx, y + dy

            if 0 <= ny < len(self.grid) and 0 <= nx < len(self.grid[ny]):
                if self.grid[ny][nx] == 2: 
                    self.grid[ny][nx] = 0  
                    
                     # Se houver um poder naquela posição, coloca-o no mapa
                    if (ny, nx) in self.power_positions:
                        self.place_power((ny, nx))
                        self.power_positions.remove((ny, nx))

    def get_grid(self):

        """Retorna o estado atual do mapa."""

        return self.grid
    
    def get_stage(self):

        """Retorna o nome do estágio atual."""
        
        return self.stage_name
    
    def reset_grid(self):

        """Reseta o grid para o estado inicial e recalcula as posições dos poderes."""

        self.grid = copy.deepcopy(self.initial_grid)  # Reseta o grid para o estado inicial
        self.power_positions = []  # Limpa as posições dos poderes antigos
        self.generate_power_positions()  # Gera novas posições para os poderes
        