import pygame
import sys
import random
import math

from config.constants import *

class Menu:

    def __init__(self):
        
        # Inicialização do Pygame
        pygame.init()

        # Configurações da janela
        self.SCREEN_WIDTH, self.SCREEN_HEIGHT = 800, 600
        self.screen = pygame.display.set_mode((self.SCREEN_WIDTH, self.SCREEN_HEIGHT))
        pygame.display.set_caption("Menu - Bomberman Style")

        # Cores
        self.WHITE = (255, 255, 255)
        self.BLACK = (0, 0, 0)
        self.HIGHLIGHT = (255, 200, 0)
        self.GRAY = (50, 50, 50)
        self.BLUE = (0, 100, 255)

        # Fonte
        self.font = pygame.font.Font(None, 50)
        self.small_font = pygame.font.Font(None, 36)

        # Itens do menu
        self.menu_items = ["Iniciar", "Creditos", "Sair"]
        self.selected_item = 0  # Item atualmente selecionado
        self.menu_positions = []

        # Valores padrão para IP e porta
        self.default_ip = SERVER_IP  # IP padrão
        self.default_port = SERVER_PORT   # Porta padrão

        self.background_image = pygame.image.load(PATH_BACKGROUND)
        self.background_image = pygame.transform.scale(self.background_image, (self.SCREEN_WIDTH, self.SCREEN_HEIGHT))
        self.default_port = str(SERVER_PORT)

        self.animation_offset = 0
        self.title_scale = 1.0
        
        # Configuração da animação da bomba
        self.bomb_icon = pygame.image.load("client/assets/icons/bomb.png")
        self.bomb_icon = pygame.transform.scale(self.bomb_icon, (32, 32))
        self.bomb_animation_frame = 0
        self.last_bomb_update = pygame.time.get_ticks()
        self.bomb_update_delay = 200  # Tempo entre frames da animação em millisegundos
        self.bomb_rotation = 0  # Para rotação da bomba

    def create_particle(self):
        return {
            'x': random.randint(0, self.SCREEN_WIDTH),
            'y': random.randint(0, self.SCREEN_HEIGHT),
            'speed': random.uniform(1, 3),
            'size': random.randint(2, 5),
            'color': random.choice([(255, 165, 0), (255, 69, 0), (255, 140, 0)])  # Tons de laranja
        }

    def draw_text(self, text, font, color, center):
        """Desenha um texto centralizado."""
        if not isinstance(text, str):  # Garantir que o texto seja uma string
            text = str(text)
        text_surface = font.render(text, True, color)
        text_rect = text_surface.get_rect(center=center)
        self.screen.blit(text_surface, text_rect)

    def draw_menu(self):
        # Desenhar fundo (agora estático)
        self.screen.blit(self.background_image, (0, 0))

        # Título (sem animação de escala)
        title_text = "BOMBERMAN"
        title_font = pygame.font.Font(None, 100)
        title_surf = title_font.render(title_text, True, (255, 255, 0))
        title_rect = title_surf.get_rect(center=(self.SCREEN_WIDTH // 2, 100))
        
        # Sombra do título
        shadow_surf = title_font.render(title_text, True, (100, 100, 0))
        shadow_rect = shadow_surf.get_rect(center=(self.SCREEN_WIDTH // 2 + 4, 104))
        self.screen.blit(shadow_surf, shadow_rect)
        self.screen.blit(title_surf, title_rect)

        # Animação da bomba
        current_time = pygame.time.get_ticks()
        if current_time - self.last_bomb_update > self.bomb_update_delay:
            self.bomb_rotation = (self.bomb_rotation + 90) % 360  # Rotaciona 90 graus
            self.last_bomb_update = current_time

        # Desenhar bombas animadas nos lados do título
        rotated_bomb = pygame.transform.rotate(self.bomb_icon, self.bomb_rotation)
        bomb_rect = rotated_bomb.get_rect()
        
        # Posição das bombas
        left_bomb_pos = (title_rect.left - 60, title_rect.centery - bomb_rect.height // 2)
        right_bomb_pos = (title_rect.right + 20, title_rect.centery - bomb_rect.height // 2)
        
        self.screen.blit(rotated_bomb, left_bomb_pos)
        self.screen.blit(rotated_bomb, right_bomb_pos)

        # Desenhar itens do menu (manter o código existente dos itens do menu)
        self.menu_positions = []
        for i, item in enumerate(self.menu_items):
            is_selected = i == self.selected_item
            item_color = self.HIGHLIGHT if is_selected else self.WHITE
            
            # Calcular posição base
            base_y = self.SCREEN_HEIGHT // 2 + i * 80
            offset = math.sin(pygame.time.get_ticks() * 0.004 + i) * 5 if is_selected else 0
            
            # Criar superfície do texto
            text_surf = self.font.render(item, True, item_color)
            text_rect = text_surf.get_rect(center=(self.SCREEN_WIDTH // 2, base_y + offset))
            
            # Desenhar fundo do item
            padding = 20
            background_rect = pygame.Rect(text_rect.x - padding,
                                        text_rect.y - padding//2,
                                        text_rect.width + padding * 2,
                                        text_rect.height + padding)
            
            # Gradiente para o fundo do item
            if is_selected:
                gradient_colors = [(50, 50, 150), (30, 30, 100)]
            else:
                gradient_colors = [(30, 30, 30), (20, 20, 20)]
                
            for j in range(background_rect.height):
                progress = j / background_rect.height
                color = [int(a + (b - a) * progress) for a, b in zip(gradient_colors[0], gradient_colors[1])]
                pygame.draw.line(self.screen, color,
                            (background_rect.left, background_rect.top + j),
                            (background_rect.right, background_rect.top + j))
            
            # Borda do item
            pygame.draw.rect(self.screen, item_color, background_rect, 2, border_radius=10)
            
            # Desenhar ícone da bomba se selecionado
            if is_selected:
                bomb_pos = (text_rect.left - 40, text_rect.centery - self.bomb_icon.get_height()//2)
                self.screen.blit(self.bomb_icon, bomb_pos)
                bomb_pos = (text_rect.right + 10, text_rect.centery - self.bomb_icon.get_height()//2)
                self.screen.blit(self.bomb_icon, bomb_pos)
            
            # Desenhar texto
            self.screen.blit(text_surf, text_rect)
            self.menu_positions.append(text_rect)

    def menu_loop(self):
        """Loop do menu principal."""
        while True:
            current_time = pygame.time.get_ticks()
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    pygame.quit()
                    sys.exit()
                elif event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_UP:
                        self.selected_item = (self.selected_item - 1) % len(self.menu_items)  # Navegar para cima
                    elif event.key == pygame.K_DOWN:
                        self.selected_item = (self.selected_item + 1) % len(self.menu_items)  # Navegar para baixo
                    elif event.key == pygame.K_RETURN:
                        if self.selected_item == 0:
                            ip, port, name = self.connection_screen()
                            if ip and port and name:
                                from core.game import Game
                                game = Game(ip, int(port))
                                game.player_manager.local_player.name = name  # Define o nome do jogador local
                                game.run()
                                del game
                                game = None
                                pygame.quit()
                                pygame.init()
                                self.__init__()
                        elif self.selected_item == 1:
                            self.credits_screen()
                        elif self.selected_item == 2:
                            pygame.quit()
                            sys.exit()
                elif event.type == pygame.MOUSEMOTION:
                    mouse_pos = pygame.mouse.get_pos()
                    for i, rect in enumerate(self.menu_positions):
                        if rect.collidepoint(mouse_pos):
                            self.selected_item = i
                elif event.type == pygame.MOUSEBUTTONDOWN:
                    if event.button == 1:
                        if self.selected_item == 0:
                            ip, port, name = self.connection_screen()
                            if ip and port and name:
                                from core.game import Game
                                game = Game(ip, int(port), name)
                                pygame.quit()
                                pygame.init()
                                self.__init__()
                        elif self.selected_item == 1:
                            self.credits_screen()
                        elif self.selected_item == 2:
                            pygame.quit()
                            sys.exit()

            self.draw_menu()
            pygame.display.flip()

    def connection_screen(self):
        """Tela para digitar IP, porta e nome do personagem."""
        ip = self.default_ip
        port = str(self.default_port)
        name = ""
        active_input = "ip"
        
        # Criar um fundo escuro semitransparente
        dark_overlay = pygame.Surface((self.SCREEN_WIDTH, self.SCREEN_HEIGHT))
        dark_overlay.fill((20, 20, 30))  # Azul muito escuro
        dark_overlay.set_alpha(230)  # Quase opaco
        
        # Definir os retângulos de entrada com posicionamento melhorado
        input_box_width = 400
        input_box_height = 50
        center_x = self.SCREEN_WIDTH // 2
        
        input_rects = {
            "ip": pygame.Rect(center_x - input_box_width//2, 180, input_box_width, input_box_height),
            "port": pygame.Rect(center_x - input_box_width//2, 280, input_box_width, input_box_height),
            "name": pygame.Rect(center_x - input_box_width//2, 380, input_box_width, input_box_height)
        }

        while True:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    pygame.quit()
                    sys.exit()
                elif event.type == pygame.MOUSEBUTTONDOWN:
                    for key, rect in input_rects.items():
                        if rect.collidepoint(event.pos):
                            active_input = key
                elif event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_RETURN:
                        if ip and port and name:
                            return ip, port, name
                    elif event.key == pygame.K_BACKSPACE:
                        if active_input == "ip":
                            ip = ip[:-1]
                        elif active_input == "port":
                            port = port[:-1]
                        elif active_input == "name":
                            name = name[:-1]
                    elif event.key == pygame.K_TAB:
                        active_input = ["ip", "port", "name"][(["ip", "port", "name"].index(active_input) + 1) % 3]
                    else:
                        if active_input == "ip" and (event.unicode.isdigit() or event.unicode == "."):
                            ip += event.unicode
                        elif active_input == "port" and event.unicode.isdigit():
                            port += event.unicode
                        elif active_input == "name" and event.unicode.isalpha() and len(name) < 3:
                            name += event.unicode.upper()

            # Desenhar fundo
            self.screen.blit(self.background_image, (0, 0))
            self.screen.blit(dark_overlay, (0, 0))

            # Container central
            container_rect = pygame.Rect(center_x - 300, 80, 600, 500)
            pygame.draw.rect(self.screen, (30, 30, 40), container_rect, border_radius=15)
            pygame.draw.rect(self.screen, self.HIGHLIGHT, container_rect, 2, border_radius=15)

            # Título
            title_text = "Enter Server Details"
            title_shadow = self.font.render(title_text, True, (0, 0, 0))
            title = self.font.render(title_text, True, self.HIGHLIGHT)
            self.screen.blit(title_shadow, (center_x - title.get_width()//2 + 2, 102))
            self.screen.blit(title, (center_x - title.get_width()//2, 100))

            # Campos de entrada
            labels = ["IP Address:", "Port:", "Name (3 letters):"]
            values = [ip, port, name]
            
            for i, (label, value, (input_key, rect)) in enumerate(zip(labels, values, input_rects.items())):
                # Label
                label_surf = self.small_font.render(label, True, self.WHITE)
                self.screen.blit(label_surf, (rect.left, rect.top - 25))
                
                # Campo de entrada
                pygame.draw.rect(self.screen, (40, 40, 50), rect, border_radius=8)
                pygame.draw.rect(self.screen, 
                            self.HIGHLIGHT if active_input == input_key else (100, 100, 100),
                            rect, 2, border_radius=8)
                
                # Texto do campo
                text_surf = self.small_font.render(value, True, self.WHITE)
                text_rect = text_surf.get_rect(midleft=(rect.left + 10, rect.centery))
                self.screen.blit(text_surf, text_rect)

            # Botões
            button_width = 200
            button_height = 50
            spacing = 20
            
            buttons = [
                ("Confirm", pygame.Rect(center_x - button_width - spacing//2, 460, button_width, button_height)),
                ("Back", pygame.Rect(center_x + spacing//2, 460, button_width, button_height))
            ]

            for text, button in buttons:
                # Fundo do botão
                pygame.draw.rect(self.screen, (40, 40, 50), button, border_radius=8)
                pygame.draw.rect(self.screen, self.HIGHLIGHT, button, 2, border_radius=8)
                
                # Texto do botão
                button_text = self.small_font.render(text, True, self.WHITE)
                text_rect = button_text.get_rect(center=button.center)
                self.screen.blit(button_text, text_rect)

                # Hover effect
                if button.collidepoint(pygame.mouse.get_pos()):
                    pygame.draw.rect(self.screen, (60, 60, 70), button, border_radius=8)
                    self.screen.blit(button_text, text_rect)
                    
                    if pygame.mouse.get_pressed()[0]:
                        if text == "Confirm" and ip and port and name:
                            return ip, port, name
                        elif text == "Back":
                            return None, None, None

            pygame.display.flip()

    def credits_screen(self):
        """Tela para exibir os créditos do jogo."""
        # Criar um fundo escuro semitransparente
        dark_overlay = pygame.Surface((self.SCREEN_WIDTH, self.SCREEN_HEIGHT))
        dark_overlay.fill((20, 20, 30))  
        dark_overlay.set_alpha(230)  

        credits = [
            "Criadores:",
            "Gabriel Afonso Barbosa",
            "Yury Araujo",
            "Igor Augusto",
            "Michele",
            "Miller",
            "Pedro",
            "",  
            "Obs: \"é só uma matriz\" - Igor Augusto" 
        ]

        scroll_y = self.SCREEN_HEIGHT 
        scroll_speed = 2  

        while True:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    pygame.quit()
                    sys.exit()
                elif event.type == pygame.MOUSEBUTTONDOWN or event.type == pygame.KEYDOWN:
                    return  

            # Desenhar fundo
            self.screen.blit(self.background_image, (0, 0))
            self.screen.blit(dark_overlay, (0, 0))

            # Container central
            container_rect = pygame.Rect(self.SCREEN_WIDTH // 2 - 300, 50, 600, self.SCREEN_HEIGHT - 100)
            pygame.draw.rect(self.screen, (30, 30, 40), container_rect, border_radius=15)
            pygame.draw.rect(self.screen, self.HIGHLIGHT, container_rect, 2, border_radius=15)

            # Título
            title_text = "Créditos"
            title_shadow = self.font.render(title_text, True, (0, 0, 0))
            title = self.font.render(title_text, True, self.HIGHLIGHT)
            title_pos = (self.SCREEN_WIDTH // 2, 80)
            self.screen.blit(title_shadow, (title_pos[0] - title.get_width()//2 + 2, title_pos[1] + 2))
            self.screen.blit(title, (title_pos[0] - title.get_width()//2, title_pos[1]))

            # Desenhar créditos com efeito de rolagem
            for i, credit in enumerate(credits):
                y_pos = scroll_y + i * 50
                if 120 < y_pos < self.SCREEN_HEIGHT - 60:
                    if i == 0:  
                        text_surf = self.font.render(credit, True, self.HIGHLIGHT)
                    elif i == len(credits) - 1:  
                        text_surf = self.small_font.render(credit, True, self.HIGHLIGHT)
                    else:
                        text_surf = self.small_font.render(credit, True, self.WHITE)
                    text_rect = text_surf.get_rect(center=(self.SCREEN_WIDTH // 2, y_pos))
                    self.screen.blit(text_surf, text_rect)

            # Atualizar posição de rolagem
            scroll_y -= scroll_speed
            if scroll_y < -len(credits) * 50:
                scroll_y = self.SCREEN_HEIGHT

            # Instrução para voltar
            back_text = "Pressione qualquer tecla para voltar"
            back_surf = self.small_font.render(back_text, True, self.WHITE)
            back_rect = back_surf.get_rect(center=(self.SCREEN_WIDTH // 2, self.SCREEN_HEIGHT - 30))
            self.screen.blit(back_surf, back_rect)

            pygame.display.flip()
            pygame.time.wait(20)  # Pequena pausa para controlar a velocidade de rolagem
