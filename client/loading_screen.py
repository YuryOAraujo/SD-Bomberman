import pygame
from constants import WIDTH, HEIGHT, WHITE, BLACK

class LoadingScreen:
    def __init__(self, screen):
        """
        Inicializa a tela de carregamento.

        :param screen: Superfície do Pygame onde a tela será desenhada.
        """
        self.screen = screen
        self.font = pygame.font.Font(None, 36)  # Fonte para o texto
        self.players_connected = 0  # Número de jogadores conectados
        self.total_players = 4  # Total de jogadores necessários

    def draw(self):
        """
        Desenha a tela de carregamento.
        """
        # Limpa a tela com uma cor de fundo
        self.screen.fill(BLACK)

        # Texto principal
        text = self.font.render("Aguardando jogadores...", True, WHITE)
        text_rect = text.get_rect(center=(WIDTH // 2, HEIGHT // 2 - 50))
        self.screen.blit(text, text_rect)

        # Texto com o número de jogadores conectados
        players_text = self.font.render(f"Jogadores conectados: {self.players_connected}/{self.total_players}", True, WHITE)
        players_rect = players_text.get_rect(center=(WIDTH // 2, HEIGHT // 2))
        self.screen.blit(players_text, players_rect)

        # Atualiza a tela
        pygame.display.flip()

    def update_players_connected(self, players_connected):
        """
        Atualiza o número de jogadores conectados.

        :param players_connected: Número de jogadores conectados.
        """
        self.players_connected = players_connected