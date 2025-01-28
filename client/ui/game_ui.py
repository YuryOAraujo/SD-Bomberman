import pygame
from config.constants import *

# Cores (defina conforme necessário)
WHITE = (255, 255, 255)
RED = (255, 0, 0)

class GameUI:

    def __init__(self, screen, players, ui_width, map_width, player_images):

        """
        Inicializa a interface do usuário do jogo.

        :param screen: Superfície do Pygame onde a interface será desenhada.
        :param players: Lista ou grupo de jogadores para exibir informações.
        :param ui_width: Largura da área da interface.
        :param map_width: Largura do mapa (para calcular o deslocamento da interface).
        :param player_images: Lista de imagens dos personagens virados para frente.
        """

        self.screen = screen
        self.players = players
        self.ui_width = ui_width
        self.map_width = map_width

         # Imagens dos personagens virados para frente
        self.player_images = player_images 

        # Fonte para texto
        self.font = pygame.font.Font(None, 36)  

        # Carrega a imagem do coração (vida)
        try:
            self.heart_image = pygame.image.load(PATH_ICON_HEART).convert_alpha()

             # Redimensiona para 32x32 pixels
            self.heart_image = pygame.transform.scale(self.heart_image, (32, 32)) 
        except FileNotFoundError:
            print("Erro: Arquivo 'heart.png' não encontrado. Usando fallback.")

            # Fallback: superfície vazia
            self.heart_image = pygame.Surface((32, 32))  

            # Preenche com vermelho
            self.heart_image.fill((255, 0, 0))  

    def draw(self, time_left):

        """
        Desenha a interface do usuário na tela.

        :param time_left: Tempo restante para o fim do jogo.
        """

        # Define a cor de fundo da interface (cinza médio)
        interface_bg_color = (169, 169, 169)
        pygame.draw.rect(self.screen, interface_bg_color, (self.map_width, 0, self.ui_width, HEIGHT))

        # Desenhar o tempo restante
        time_text = self.font.render(f"Tempo: {time_left}", True, WHITE)
        self.screen.blit(time_text, (self.map_width + 10, 10))  # Posiciona o tempo no topo da área da interface

        # Desenhar as fotos e a vida dos personagens
        for i, player in enumerate(self.players):

            # Posição base para cada jogador
            base_x = self.map_width + 10  # Margem à esquerda da interface
            base_y = 50 + i * 100  # Espaçamento vertical entre os jogadores

            # Desenhar a imagem do personagem (virado para frente)
            if i < len(self.player_images):  # Verifica se o índice é válido
                self.screen.blit(self.player_images[i], (base_x, base_y))
            else:
                print(f"Erro: Índice {i} fora do intervalo da lista de imagens dos personagens.")

            # Desenhar a vida do personagem (corações)
            if hasattr(player, 'health'):
                for h in range(player.health):
                    self.screen.blit(self.heart_image, (base_x + 70 + h * 35, base_y + 20))  # Posiciona os corações ao lado da foto
            else:
                print(f"Erro: O jogador {i} não possui o atributo 'health'.")