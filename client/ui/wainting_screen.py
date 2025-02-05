import pygame

class WaitingScreen:

    def __init__(self, screen, player_manager):

        self.screen = screen
        self.clock = pygame.time.Clock()
        self.font_title = pygame.font.Font(None, 48)
        self.font_table = pygame.font.Font(None, 36)
        self.player_manager = player_manager

    def draw(self):

        """Desenha a tela de espera com a tabela de jogadores e status."""

        self.screen.fill((30, 30, 30))  # Fundo cinza escuro

        # Mensagem principal
        title_text = self.font_title.render("Aguardando jogadores...", True, (255, 255, 255))
        self.screen.blit(title_text, (self.screen.get_width() // 2 - 200, 50))

        # Cabeçalho da tabela
        header_player = self.font_table.render("Jogador", True, (255, 255, 255))
        header_status = self.font_table.render("Status", True, (255, 255, 255))
        self.screen.blit(header_player, (150, 150))
        self.screen.blit(header_status, (400, 150))

        # Desenhar linha separadora
        pygame.draw.line(self.screen, (255, 255, 255), (140, 190), (550, 190), 3)

        # Listar jogadores conectados
        players = self.player_manager.players
        y_offset = 200  # Primeira linha após o cabeçalho

        for player in players:
            player_status = "Conectado" if not player.eliminated else "Aguardando"
            color = (0, 255, 0) if player_status == "Conectado" else (255, 0, 0)

            # Renderiza nome e status
            player_text = self.font_table.render(player.name, True, (255, 255, 255))
            status_text = self.font_table.render(player_status, True, color)

            # Posiciona os textos
            self.screen.blit(player_text, (150, y_offset))
            self.screen.blit(status_text, (400, y_offset))
            
            # Linha separadora entre jogadores
            pygame.draw.line(self.screen, (100, 100, 100), (140, y_offset + 35), (550, y_offset + 35), 2)

            y_offset += 50  # Espaçamento entre linhas

        pygame.display.update()

    def wait_for_game_start(self):
        """Mostra a tela de espera até que o jogo seja iniciado pelo servidor."""
        running = True
        while running:
            self.draw()  # Atualiza a tela com a tabela de jogadores

            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    pygame.quit()
                    return False  # Sai do jogo

            self.clock.tick(30)  # Controle de FPS
        return True