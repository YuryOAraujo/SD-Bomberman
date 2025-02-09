import pygame
import math
from config.constants import *
from utils.map import Map

class GameUI:

    def __init__(self, screen, players, ui_width, map_width):

        self.screen = screen
        self.players = players
        self.ui_width = ui_width
        self.map_width = map_width

        self.show_help_modal = False
        self.help_rect = None
        self.close_button_rect = None

        self.power_icons = Map.load_power_animations()

        # Carrega a imagem do troféu
        try:
            self.trophy_image = pygame.image.load(PATH_TROPHY).convert_alpha()
            self.trophy_image = pygame.transform.scale(self.trophy_image, (24, 24))
        except FileNotFoundError:
            self.trophy_image = pygame.Surface((24, 24))
            self.trophy_image.fill((255, 215, 0))

        # Fontes
        self.title_font = pygame.font.Font(None, 36)
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
            title_rect = title_surf.get_rect(midtop=(rect.centerx, rect.top + 20)) 
            self.screen.blit(title_surf, title_rect)

    def update_players_data(self, new_player_data):
        
        """
        Atualiza todas as informações dos jogadores no meio do jogo.

        Args:
            new_player_data (dict): Um dicionário contendo os dados atualizados de todos os jogadores.
        """

        self.players = new_player_data

    def draw(self, current_round=1):
        
        # Fundo principal
        pygame.draw.rect(self.screen, self.bg_color, (self.map_width, 0, self.ui_width, HEIGHT))

        # Painel de jogadores
        players_panel = pygame.Rect(self.map_width + 20, 20, self.ui_width - 40, HEIGHT - 60)
        self.draw_panel(players_panel, "JOGADORES")

        # Desenhar informações dos jogadores
        for i, player in enumerate(self.players):
            
            base_y = 80 + i * 120  # Aumentado o espaçamento vertical
            
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
        
        # --- PAINEL INFERIOR ---
        footer_height = 60
        footer_rect = pygame.Rect(0, HEIGHT - footer_height, self.map_width + self.ui_width, footer_height)
        pygame.draw.rect(self.screen, self.panel_color, footer_rect)
        pygame.draw.rect(self.screen, self.highlight_color, footer_rect, 2)

        # Texto do jogo e Round
        game_title = self.title_font.render("SD-Bomberman", True, self.highlight_color)
        game_title_rect = game_title.get_rect(midleft=(20, HEIGHT - footer_height // 2))
        self.screen.blit(game_title, game_title_rect)

        round_footer_text = self.font.render(f"Round {current_round}", True, self.highlight_color)
        round_footer_rect = round_footer_text.get_rect(midleft=(game_title_rect.right + 250, HEIGHT - footer_height // 2))
        self.screen.blit(round_footer_text, round_footer_rect)

        # Ícone de ajuda
        help_icon = pygame.image.load(PATH_TROPHY)  # Supondo que há um ícone de ajuda
        help_icon = pygame.transform.scale(help_icon, (32, 32))
        self.help_rect = help_icon.get_rect(midright=(self.map_width + self.ui_width - 50, HEIGHT - footer_height // 2))
        self.screen.blit(help_icon, self.help_rect)

        if self.show_help_modal:
           self.draw_help_modal()

    def handle_event(self, event):

        if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
            if self.help_rect and self.help_rect.collidepoint(event.pos):
                self.show_help_modal = True
            elif self.show_help_modal and self.close_button_rect and self.close_button_rect.collidepoint(event.pos):
                self.show_help_modal = False

    def draw_help_modal(self):

        modal_width, modal_height = 600, 500
        modal_x = (self.map_width + self.ui_width - modal_width) // 2
        modal_y = (HEIGHT - modal_height) // 2
        modal_rect = pygame.Rect(modal_x, modal_y, modal_width, modal_height)

        # Fundo com bordas arredondadas
        pygame.draw.rect(self.screen, self.panel_color, modal_rect, border_radius=12)
        pygame.draw.rect(self.screen, self.highlight_color, modal_rect, 3, border_radius=12)

        # Título
        title_surface = self.font.render("Informações do Jogo", True, self.highlight_color)
        self.screen.blit(title_surface, (modal_rect.x + (modal_width - title_surface.get_width()) // 2, modal_rect.y + 40))

        # Texto explicativo
        help_text = [
            "Objetivo: Vença 3 rounds para ganhar o jogo!", 
            "Dicas: Pegue poderes espalhados pelo mapa para", 
            "melhorar suas habilidades!"
        ]

        text_start_y = modal_rect.y + 100

        for i, line in enumerate(help_text):
            text_surface = self.small_font.render(line, True, self.text_color)
            self.screen.blit(text_surface, (modal_rect.x + 40, text_start_y + i * 30)) 

        # Criando a tabela de poderes
        table_x, table_y = modal_rect.x + 40, text_start_y + 110
        col_widths = [50, 150]
        row_height = 55

        headers = ["Ícone", "Descrição do Poder"]
        header_color = self.highlight_color

        for i, header in enumerate(headers):
            text_surface = self.small_font.render(header, True, header_color)
            self.screen.blit(text_surface, (table_x + i * col_widths[i], table_y))

        line_y = table_y + 30 
        pygame.draw.rect(self.screen, self.highlight_color, pygame.Rect(table_x, line_y, sum(col_widths), 2))

        descriptions = {
            "flame": ["Aumenta o alcance", "da explosão das bombas."],
            "bomb": ["Permite posicionar", "múltiplas bombas."],
            "speed": ["Aumenta a velocidade", "para movimentação rápida."],
        }

        max_rows = (modal_height - (table_y - modal_rect.y) - 30) // row_height
        for i, (name, desc_lines) in enumerate(descriptions.items()):
            if i >= max_rows:
                break
            icon = self.power_icons.get(name)
            if icon:
                self.screen.blit(icon, (table_x + 2, table_y + 45 + i * row_height))
            
            for j, desc in enumerate(desc_lines):
                text_surface = self.small_font.render(desc, True, self.text_color)
                self.screen.blit(text_surface, (table_x + col_widths[0] + 97, table_y + 45 + i * row_height + j * 20))

        # Botão de fechar
        self.close_button_rect = pygame.Rect(modal_rect.right - 45, modal_rect.y + 15, 30, 30)
        pygame.draw.rect(self.screen, (220, 50, 50), self.close_button_rect, border_radius=8)
        close_text = self.small_font.render("X", True, (255, 255, 255))
        self.screen.blit(close_text, (self.close_button_rect.x + 10, self.close_button_rect.y + 8))

