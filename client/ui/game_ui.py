import pygame
import math
from config.constants import *

class GameUI:

    def __init__(self, screen, players, ui_width, map_width, trophy_image_path):

        self.screen = screen
        self.players = players
        self.ui_width = ui_width
        self.map_width = map_width

        # Carrega a imagem do troféu
        try:
            self.trophy_image = pygame.image.load("client/assets/icons/trofeu.png").convert_alpha()
            self.trophy_image = pygame.transform.scale(self.trophy_image, (24, 24))
        except FileNotFoundError:
            self.trophy_image = pygame.Surface((24, 24))
            self.trophy_image.fill((255, 215, 0))

        # Fontes
        self.title_font = pygame.font.Font(None, 48)
        self.font = pygame.font.Font(None, 36)
        self.small_font = pygame.font.Font(None, 24)

        # Cores
        self.bg_color = (30, 30, 40)  # Azul escuro
        self.panel_color = (40, 40, 50)  # Azul um pouco mais claro
        self.highlight_color = (255, 200, 0)  # Amarelo
        self.text_color = (255, 255, 255)  # Branco

    def draw_panel(self, rect, title=None):

        """Desenha um painel estilizado com borda arredondada"""
        
        pygame.draw.rect(self.screen, self.panel_color, rect, border_radius=10)
        pygame.draw.rect(self.screen, self.highlight_color, rect, 2, border_radius=10)
        
        if title:
            title_surf = self.small_font.render(title, True, self.highlight_color)
            title_rect = title_surf.get_rect(midtop=(rect.centerx, rect.top + 5))
            self.screen.blit(title_surf, title_rect)

    def update_players_data(self, new_player_data):
        
        """
        Atualiza todas as informações dos jogadores no meio do jogo.

        Args:
            new_player_data (dict): Um dicionário contendo os dados atualizados de todos os jogadores.
        """
        self.players = new_player_data  # Atualiza a referência para os novos jogadores

    def draw(self):
        
        # Fundo principal
        pygame.draw.rect(self.screen, self.bg_color, (self.map_width, 0, self.ui_width, HEIGHT))

        # Painel de jogadores
        players_panel = pygame.Rect(self.map_width + 20, 20, self.ui_width - 40, HEIGHT - 40)
        self.draw_panel(players_panel, "JOGADORES")

        # Desenhar informações dos jogadores
        for i, player in enumerate(self.players):
            base_y = 70 + i * 120  # Aumentado o espaçamento vertical
            
            # Fundo do jogador
            player_rect = pygame.Rect(self.map_width + 40, base_y, self.ui_width - 80, 100)
            is_alive = not getattr(player, 'eliminated', False)
            player_bg_color = self.panel_color if is_alive else (60, 30, 30)
            pygame.draw.rect(self.screen, player_bg_color, player_rect, border_radius=8)
            pygame.draw.rect(self.screen, self.highlight_color, player_rect, 2, border_radius=8)

            # Nome do jogador
            if hasattr(player, 'name'):
                name_text = self.font.render(player.name, True, self.text_color)
                self.screen.blit(name_text, (player_rect.left + 10, base_y + 10))

            # Sprite do jogador
            if hasattr(player, 'animations') and "down" in player.animations:
                sprite = player.animations["down"][0]
                sprite_rect = sprite.get_rect(midleft=(player_rect.left + 50, base_y + 60))
                self.screen.blit(sprite, sprite_rect)

            # Troféus com efeito de brilho
            if hasattr(player, 'round_wins'):
                trophy_start_x = player_rect.right - 40 - (player.round_wins * 30)
                for t in range(player.round_wins):
                    # Efeito de brilho
                    glow_size = abs(math.sin(pygame.time.get_ticks() * 0.003 + t)) * 4
                    glow_surf = pygame.Surface((28, 28), pygame.SRCALPHA)
                    pygame.draw.circle(glow_surf, (255, 215, 0, 100), (14, 14), 12 + glow_size)
                    self.screen.blit(glow_surf, (trophy_start_x + t * 30 - 2, base_y + 50 - 2))
                    
                    # Troféu
                    self.screen.blit(self.trophy_image, (trophy_start_x + t * 30, base_y + 50))

            # Status do jogador
            status_text = "VIVO" if is_alive else "ELIM."
            status_color = (100, 255, 100) if is_alive else (255, 100, 100)
            status_surf = self.small_font.render(status_text, True, status_color)
            self.screen.blit(status_surf, (player_rect.right - 80, base_y + 10))