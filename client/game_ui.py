import pygame
from constants import WIDTH, HEIGHT

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
        :param player_images: Lista de imagens dos personagens (fallback).
        """
        self.screen = screen
        self.players = players
        self.ui_width = ui_width
        self.map_width = map_width
        self.player_images = player_images  # Imagens dos personagens (fallback)
        self.font = pygame.font.Font(None, 36)  # Fonte para texto

        try:
            self.trophy_image = pygame.image.load("client/graphics/trophy.png").convert_alpha()
            self.trophy_image = pygame.transform.scale(self.trophy_image, (32, 32))  # Redimensiona para 32x32 pixels
        except FileNotFoundError:
            print("Erro: Arquivo 'trophy.png' não encontrado. Usando fallback.")
            # Fallback: uma superfície vazia
            self.trophy_image = pygame.Surface((32, 32))  # Tamanho padrão
            self.trophy_image.fill((255, 215, 0))  # Preenche com uma cor dourada (fallback)

    def draw(self, time_left):
        """
        Desenha a interface do usuário na tela.

        :param time_left: Tempo restante para o fim do jogo.
        """
        # Define a cor de fundo da interface (cinza médio)
        interface_bg_color = (169, 169, 169)
        
        ui_x = 720  
        pygame.draw.rect(self.screen, interface_bg_color, (ui_x, 0, self.ui_width, HEIGHT))

        # Desenhar o tempo restante
        time_text = self.font.render(f"Tempo: {time_left}", True, WHITE)
        self.screen.blit(time_text, (ui_x + 10, 10)) 

        # Desenhar as fotos e os troféus dos personagens
        for i, player in enumerate(self.players):
            # Posição base para cada jogador
            base_x = ui_x + 10  
            base_y = 50 + i * 100  

            # Desenhar a sprite do personagem (usando a primeira imagem da animação "down")
            if i < len(self.player_images):  # Verifica se o índice é válido
                player_sprite = pygame.transform.scale(player.animations["down"][0], (64, 64)).convert_alpha()
                self.screen.blit(player_sprite, (base_x, base_y))
            else:
                print(f"Erro: Índice {i} fora do intervalo da lista de imagens dos personagens.")

            # Desenhar os troféus do personagem (baseado no número de vitórias)
            if hasattr(player, 'round_wins'):
                for t in range(player.round_wins):
                    # Ajuste as coordenadas dos troféus para alinhar com a sprite do personagem
                    self.screen.blit(self.trophy_image, (base_x + 70 + t * 35, base_y + 20))  # Posiciona os troféus ao lado da foto
            else:
                print(f"Erro: O jogador {i} não possui o atributo 'round_wins'.")