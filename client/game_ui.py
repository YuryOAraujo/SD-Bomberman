import pygame

# Cores (defina conforme necessário)
WHITE = (255, 255, 255)
RED = (255, 0, 0)

class GameUI:
    def __init__(self, screen, players):
        """
        Inicializa a interface do usuário do jogo.

        :param screen: Superfície do Pygame onde a interface será desenhada.
        :param players: Lista ou grupo de jogadores para exibir informações.
        """
        self.screen = screen
        self.players = players
        self.font = pygame.font.Font(None, 36)  # Fonte para texto
        self.heart_image = pygame.image.load("client/graphics/heart.png")  # Imagem do coração (vida)
        self.character_images = [
            pygame.image.load("E:/T.S.I/Estagio/SIte_IF_AVE/SD-Bomberman/client/graphics/Fundo.png"),  # Imagens dos personagens
            pygame.image.load("E:/T.S.I/Estagio/SIte_IF_AVE/SD-Bomberman/client/graphics/Fundo.png"),
            pygame.image.load("E:/T.S.I/Estagio/SIte_IF_AVE/SD-Bomberman/client/graphics/Fundo.png"),
            pygame.image.load("E:/T.S.I/Estagio/SIte_IF_AVE/SD-Bomberman/client/graphics/Fundo.png")
        ]

    def draw(self, time_left):
        """
        Desenha a interface do usuário na tela.

        :param time_left: Tempo restante para o fim do jogo.
        """
        # Desenhar o tempo restante
        time_text = self.font.render(f"Tempo: {time_left}", True, WHITE)
        self.screen.blit(time_text, (10, 10))

        # Desenhar as fotos e a vida dos personagens
        for i, player in enumerate(self.players):
            # Desenhar a imagem do personagem
            self.screen.blit(self.character_images[i], (10, 50 + i * 100))

            # Desenhar a barra de vida
            pygame.draw.rect(self.screen, RED, (60, 70 + i * 100, player.health * 2, 20))
            for h in range(player.health):
                self.screen.blit(self.heart_image, (60 + h * 30, 70 + i * 100))