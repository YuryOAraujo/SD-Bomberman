import pygame
import time
import math

class WaitingScreen:

    def __init__(self, screen, network):
        self.screen = screen
        self.clock = pygame.time.Clock()
        self.font_title = pygame.font.Font(None, 48)
        self.font_table = pygame.font.Font(None, 36)
        self.network = network
        self.animation_frame = 0  # Contador de frames para animações

    def create_gradient_background(self, width, height, start_color, end_color):
        """Cria um fundo de gradiente vertical."""
        background = pygame.Surface((width, height))
        for y in range(height):
            r = start_color[0] + (end_color[0] - start_color[0]) * y / height
            g = start_color[1] + (end_color[1] - start_color[1]) * y / height
            b = start_color[2] + (end_color[2] - start_color[2]) * y / height
            pygame.draw.line(background, (int(r), int(g), int(b)), (0, y), (width, y))
            
        return background

    def draw(self, players, loading=False, progress=0):
        """Desenha a tela de espera com animações e layout interativo."""
        screen_width, screen_height = self.screen.get_size()

        # Fundo gradiente animado
        gradient = self.create_gradient_background(screen_width, screen_height, (30, 30, 30), (10, 10, 50))
        self.screen.blit(gradient, (0, 0))

        # Título centralizado
        title_text = self.font_title.render("Aguardando jogadores...", True, (255, 255, 255))
        self.screen.blit(title_text, (screen_width // 2 - title_text.get_width() // 2, 50))

        if not loading:
            # Posicionamento dos jogadores em um círculo
            center_x, center_y = screen_width // 2, screen_height // 2
            radius = min(screen_width, screen_height) // 4  # Raio do círculo (reduzido para deixar o círculo menor)
            num_players = len(players)
            angle_step = 360 / num_players if num_players > 0 else 0

            # Desenhar cada jogador no círculo
            for i, (player_name, player_data) in enumerate(players.items()):
                player_name = str(player_data["name"])
                player_status = "Conectado" if player_data["connected"] else "Aguardando"
                color = (0, 255, 0) if player_data["connected"] else (255, 0, 0)

                # Calcular posição no círculo
                angle = math.radians(i * angle_step + self.animation_frame * 0.5)  # Ângulo + animação
                x = center_x + int(radius * math.cos(angle))
                y = center_y + int(radius * math.sin(angle))

                # Desenhar a sprite do jogador (animada)
                if "sprints" in player_data:
                    animation = player_data["sprints"]["down"]  # Usa a animação "down"
                    frame_index = int(self.animation_frame) % len(animation)  # Alterna entre os frames
                    player_sprite = animation[frame_index]
                    self.screen.blit(player_sprite, (x - player_sprite.get_width() // 2, y - player_sprite.get_height() // 2))

                # Desenhar nome e status do jogador
                player_text = self.font_table.render(player_name, True, (255, 255, 255))
                status_text = self.font_table.render(player_status, True, color)
                self.screen.blit(player_text, (x - player_text.get_width() // 2, y + 40))
                self.screen.blit(status_text, (x - status_text.get_width() // 2, y + 70))
        else:
            # Alinhar os jogadores horizontalmente durante o carregamento
            num_players = len(players)
            spacing = screen_width // (num_players + 1)  # Espaçamento entre os jogadores
            y_offset = screen_height // 2  # Posição vertical fixa

            for i, (player_name, player_data) in enumerate(players.items()):
                player_name = str(player_data["name"])
                player_status = "Conectado" if player_data["connected"] else "Aguardando"
                color = (0, 255, 0) if player_data["connected"] else (255, 0, 0)

                # Calcular posição horizontal
                x = spacing * (i + 1)

                # Desenhar a sprite do jogador (animada)
                if "sprints" in player_data:
                    animation = player_data["sprints"]["down"]  # Usa a animação "down"
                    frame_index = int(self.animation_frame) % len(animation)  # Alterna entre os frames
                    player_sprite = animation[frame_index]
                    self.screen.blit(player_sprite, (x - player_sprite.get_width() // 2, y_offset - player_sprite.get_height() // 2))

                # Desenhar nome e status do jogador
                player_text = self.font_table.render(player_name, True, (255, 255, 255))
                status_text = self.font_table.render(player_status, True, color)
                self.screen.blit(player_text, (x - player_text.get_width() // 2, y_offset + 40))
                self.screen.blit(status_text, (x - status_text.get_width() // 2, y_offset + 70))

        # Barra de progresso durante o carregamento
        if loading:
            bar_width = screen_width - 100  # Largura da barra de progresso
            bar_height = 20  # Altura da barra de progresso
            bar_x = (screen_width - bar_width) // 2
            bar_y = screen_height - 50  # Posição vertical da barra

            # Desenhar o fundo da barra de progresso
            pygame.draw.rect(self.screen, (100, 100, 100), (bar_x, bar_y, bar_width, bar_height))

            # Desenhar a barra de progresso preenchida
            filled_width = int(bar_width * progress)
            pygame.draw.rect(self.screen, (0, 255, 0), (bar_x, bar_y, filled_width, bar_height))

        # Atualizar o frame da animação
        self.animation_frame += 0.1

        pygame.display.update()

    def wait_for_game_start(self, players):
        """Mostra a tela de espera até que todos os jogadores estejam conectados."""
        # Armazena os sprints dos jogadores antes do loop
        player_sprints = {}
        for player_id, player_data in players.items():
            if "sprints" in player_data:
                player_sprints[player_id] = player_data["sprints"]

        while not all(player["connected"] for player in players.values()):
            self.draw(players)

            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    self.network.disconnect()
                    pygame.quit()
                    return None

            result_players = self.network.get_state()
            if result_players is not None:
                # Preserva os sprints dos jogadores existentes
                for player_id, new_data in result_players.items():
                    if player_id in player_sprints:
                        new_data["sprints"] = player_sprints[player_id]  # Mantém os sprints armazenados
                players = result_players  # Atualiza os dados dos jogadores

            self.clock.tick(60)

        # Exibir "Carregando..." com barra de progresso por 2 segundos
        start_time = time.time()
        while time.time() - start_time < 2:
            progress = (time.time() - start_time) / 2  # Calcula o progresso (0 a 1)
            self.draw(players, loading=True, progress=progress)

            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    self.network.disconnect()
                    pygame.quit()
                    return None

            self.clock.tick(60)

        return players