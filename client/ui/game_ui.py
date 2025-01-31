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
            self.trophy_image = pygame.image.load("client/assets/icons/trofeu.png").convert_alpha()
            self.trophy_image = pygame.transform.scale(self.trophy_image, (32, 32))  # Redimensiona para 32x32 pixels
        except FileNotFoundError:
            self.trophy_image = pygame.Surface((32, 32))  # Fallback: superfície vazia
            self.trophy_image.fill((255, 215, 0))  # Preenche com cor dourada

        # Fonte para texto
        self.font = pygame.font.Font(None, 36)

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

        # Desenhar as fotos, nomes e troféus dos personagens
        for i, player in enumerate(self.players):
            # Posição base para cada jogador
            base_x = self.map_width + 10  # Margem à esquerda da interface
            base_y = 50 + i * 100  # Espaçamento vertical entre os jogadores

            # Obtém o sprite virado para frente do jogador
            if hasattr(player, 'animations') and "down" in player.animations:
                player_sprite = player.animations["down"][0]  # Primeiro frame da animação "frente"
                self.screen.blit(player_sprite, (base_x, base_y + 30))  # Ajuste para deixar espaço para o nome
            else:
                print(f"Erro: Jogador {i} não possui animações ou direção 'down'.")

            # Desenhar o nome do personagem
            if hasattr(player, 'name'):
                name_text = self.font.render(player.name, True, WHITE)
                self.screen.blit(name_text, (base_x, base_y))  # Nome acima da figura

            # Desenhar os troféus do personagem
            if hasattr(player, 'round_wins'):
                for t in range(player.round_wins):
                    self.screen.blit(self.trophy_image, (base_x + 70 + t * 35, base_y + 30))  # Posiciona os troféus ao lado da foto