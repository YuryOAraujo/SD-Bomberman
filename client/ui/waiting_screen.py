import pygame
import time

class WaitingScreen:

    def __init__(self, screen, network):
        
        self.screen = screen
        self.clock = pygame.time.Clock()
        self.font_title = pygame.font.Font(None, 48)
        self.font_table = pygame.font.Font(None, 36)
        self.network = network

    def create_gradient_background(self, width, height, start_color, end_color):
        
        """Cria um fundo de gradiente vertical."""

        background = pygame.Surface((width, height))
        for y in range(height):
            r = start_color[0] + (end_color[0] - start_color[0]) * y / height
            g = start_color[1] + (end_color[1] - start_color[1]) * y / height
            b = start_color[2] + (end_color[2] - start_color[2]) * y / height
            pygame.draw.line(background, (int(r), int(g), int(b)), (0, y), (width, y))

        return background

    def draw(self, players, loading=False):

        """Desenha a tela de espera com a tabela de jogadores e status.

        Se `loading` for True, exibe "Carregando..." no final da tela.
        """

        # Criar e aplicar o gradiente de fundo
        gradient = self.create_gradient_background(self.screen.get_width(), self.screen.get_height(), (30, 30, 30), (10, 10, 50))
        self.screen.blit(gradient, (0, 0))

        # Centralizar a tabela
        screen_width, screen_height = self.screen.get_size()
        table_x = screen_width // 2 - 200
        title_y = 50

        title_text = self.font_title.render("Aguardando jogadores...", True, (255, 255, 255))
        self.screen.blit(title_text, (screen_width // 2 - title_text.get_width() // 2, title_y))

        header_player = self.font_table.render("Jogador", True, (255, 255, 255))
        header_status = self.font_table.render("Status", True, (255, 255, 255))
        self.screen.blit(header_player, (table_x, 150))
        self.screen.blit(header_status, (table_x + 250, 150))

        pygame.draw.line(self.screen, (255, 255, 255), (table_x - 10, 190), (table_x + 350, 190), 3)

        y_offset = 200

        for player_name, player_data in players.items():
            player_name = str(player_data["name"])
            player_status = "Conectado" if player_data["connected"] else "Aguardando"
            color = (0, 255, 0) if player_data["connected"] else (255, 0, 0)

            player_text = self.font_table.render(player_name, True, (255, 255, 255))
            status_text = self.font_table.render(player_status, True, color)

            self.screen.blit(player_text, (table_x, y_offset))
            self.screen.blit(status_text, (table_x + 250, y_offset))
            pygame.draw.line(self.screen, (100, 100, 100), (table_x - 10, y_offset + 35), (table_x + 350, y_offset + 35), 2)

            y_offset += 50

        if loading:
            loading_text = self.font_title.render("Carregando...", True, (255, 255, 255))
            self.screen.blit(loading_text, (screen_width // 2 - 100, y_offset + 50))

        pygame.display.update()

    def wait_for_game_start(self, players):
        """Mostra a tela de espera até que todos os jogadores estejam conectados."""

        while not all(player["connected"] for player in players.values()):
            self.draw(players)

            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    self.network.disconnect()
                    pygame.quit()
                    return None

            result_players = self.network.get_state()
            if result_players is not None:
                players = result_players

            self.clock.tick(60)

        # Exibir "Carregando..." por 2 segundos
        start_time = time.time()
        while time.time() - start_time < 2:
            self.draw(players, loading=True)

            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    self.network.disconnect()
                    pygame.quit()
                    return None

            self.clock.tick(60)

        return players
