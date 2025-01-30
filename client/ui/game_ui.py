import pygame
from config.constants import *

class GameUI:

    def __init__(self, screen, players, ui_width, map_width, trophy_image_path):

        """
        Inicializa a interface do usuário do jogo.

        :param screen: Superfície do Pygame onde a interface será desenhada.
        :param players: Lista ou grupo de jogadores para exibir informações.
        :param ui_width: Largura da área da interface.
        :param map_width: Largura do mapa (para calcular o deslocamento da interface).
        :param trophy_image_path: Caminho para a imagem do troféu.
        """

        self.screen = screen
        self.players = players
        self.ui_width = ui_width
        self.map_width = map_width

        # Carrega a imagem do troféu
        try:
            self.trophy_image = pygame.image.load(trophy_image_path).convert_alpha()
            self.trophy_image = pygame.transform.scale(self.trophy_image, (32, 32))  # Redimensiona para 32x32 pixels
        except FileNotFoundError:
            print("Erro: Arquivo do troféu não encontrado. Usando fallback.")
            self.trophy_image = pygame.Surface((32, 32))  # Fallback: superfície vazia
            self.trophy_image.fill((255, 215, 0))  # Preenche com cor dourada

        # Fonte para texto
        self.font = pygame.font.Font(None, 36)

        # Carrega a imagem do coração (vida)
        try:
            self.heart_image = pygame.image.load(PATH_ICON_HEART).convert_alpha()
            self.heart_image = pygame.transform.scale(self.heart_image, (32, 32))  # Redimensiona para 32x32 pixels
        except FileNotFoundError:
            print("Erro: Arquivo 'heart.png' não encontrado. Usando fallback.")
            self.heart_image = pygame.Surface((32, 32))  # Fallback: superfície vazia
            self.heart_image.fill((255, 0, 0))  # Preenche com vermelho

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

        # Desenhar as fotos, vidas e troféus dos personagens
        for i, player in enumerate(self.players):
            # Posição base para cada jogador
            base_x = self.map_width + 10  # Margem à esquerda da interface
            base_y = 50 + i * 100  # Espaçamento vertical entre os jogadores

            # Obtém o sprite virado para frente do jogador
            if hasattr(player, 'animations') and "down" in player.animations:
                player_sprite = player.animations["down"][0]  # Primeiro frame da animação "frente"
                self.screen.blit(player_sprite, (base_x, base_y))
            else:
                print(f"Erro: Jogador {i} não possui animações ou direção 'down'.")

            # Desenhar a vida do personagem (corações)
            if hasattr(player, 'health'):
                for h in range(player.health):
                    self.screen.blit(self.heart_image, (base_x + 70 + h * 35, base_y + 20))  # Posiciona os corações ao lado da foto

            # Desenhar os troféus do personagem
            if hasattr(player, 'round_wins'):
                for t in range(player.round_wins):
                    self.screen.blit(self.trophy_image, (base_x + 70 + t * 35, base_y + 60))  # Posiciona os troféus abaixo dos corações