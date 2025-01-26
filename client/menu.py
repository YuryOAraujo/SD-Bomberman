import pygame
import sys

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
        self.default_ip = "127.0.0.1"  # IP padrão
        self.default_port = "5555"    # Porta padrão

        self.background_image = pygame.image.load("E:/T.S.I/Estagio/SIte_IF_AVE/SD-Bomberman/client/graphics/Fundo.png")
        self.background_image = pygame.transform.scale(self.background_image, (self.SCREEN_WIDTH, self.SCREEN_HEIGHT))

    def draw_text(self, text, font, color, center):
        """Desenha um texto centralizado."""
        text_surface = font.render(text, True, color)
        text_rect = text_surface.get_rect(center=center)
        self.screen.blit(text_surface, text_rect)

    def draw_menu(self):
        """Renderiza o menu principal com um título."""
        self.screen.blit(self.background_image, (0, 0))  # Desenha a imagem no fundo
        
        # Desenhar o título
        title_text = "Bomberman"
        self.draw_text(title_text, self.font, self.WHITE, (self.SCREEN_WIDTH // 2, 100))
        
        # Desenhar os itens do menu
        self.menu_positions = []  # Redefinir para capturar novas posições
        for i, item in enumerate(self.menu_items):
            if i == self.selected_item:
                color = self.HIGHLIGHT
            else:
                color = self.WHITE

            # Posição do texto
            text_rect = self.font.render(item, True, color).get_rect(center=(self.SCREEN_WIDTH // 2, self.SCREEN_HEIGHT // 2 + i * 60))
            
            # Fundo semitransparente
            box_rect = pygame.Rect(text_rect.x - 10, text_rect.y - 5, text_rect.width + 20, text_rect.height + 10)
            pygame.draw.rect(self.screen, self.BLACK, box_rect, border_radius=5)  # Fundo opaco (preto)
            pygame.draw.rect(self.screen, (0, 0, 0, 128), box_rect)  # Fundo semi-transparente
            
            # Desenhar o texto
            self.draw_text(item, self.font, color, text_rect.center)
            self.menu_positions.append(text_rect)

    def menu_loop(self):
        """Loop do menu principal."""
        while True:
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
                        if self.selected_item == 0:  # Quando o jogador seleciona "Iniciar"
                            ip, port = self.connection_screen()  # Obtém o IP e a porta da tela de conexão
                            if ip and port:  # Verifica se os valores são válidos
                                from game import Game  # Importa a classe Game
                                game = Game(ip, int(port))  # Passa o IP e a porta para a classe Game
                                game.run()  # Inicia o jogo
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
                    if event.button == 1:  # Clique esquerdo
                        if self.selected_item == 0:
                            ip, port = self.connection_screen()
                            if ip and port:
                                from game import Game
                                game = Game(ip, int(port))
                                game.run()
                        elif self.selected_item == 1:
                            self.credits_screen()
                        elif self.selected_item == 2:
                            pygame.quit()
                            sys.exit()

            self.draw_menu()
            pygame.display.flip()

    def connection_screen(self):
        """Tela para digitar IP e porta."""
        ip = self.default_ip  # Usar o IP padrão
        port = self.default_port  # Usar a porta padrão
        active_input = None  # Campo de entrada ativo: "ip" ou "port"
        running = True  # Controla o loop da tela de conexão

        while running:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    pygame.quit()
                    sys.exit()
                elif event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_RETURN:
                        if ip and port:
                            return ip, port  # Retorna o IP e a porta
                    elif event.key == pygame.K_BACKSPACE:
                        if active_input == "ip":
                            ip = ip[:-1]
                        elif active_input == "port":
                            port = port[:-1]
                    else:
                        if active_input == "ip":
                            # Permitir apenas números e pontos
                            if event.unicode.isdigit() or event.unicode == ".":
                                ip += event.unicode
                        elif active_input == "port":
                            # Permitir apenas números
                            if event.unicode.isdigit():
                                port += event.unicode
                elif event.type == pygame.MOUSEBUTTONDOWN:
                    if event.button == 1:  # Clique esquerdo
                        mouse_pos = pygame.mouse.get_pos()
                        if ip_box.collidepoint(mouse_pos):
                            active_input = "ip"
                        elif port_box.collidepoint(mouse_pos):
                            active_input = "port"
                        elif confirm_button.collidepoint(mouse_pos):
                            if ip and port:
                                return ip, port  # Confirmar valores e retornar
                        elif back_button.collidepoint(mouse_pos):
                            return None, None  # Voltar ao menu principal

            # Desenhar a tela
            self.screen.fill(self.GRAY)

            # Campos de texto
            self.draw_text("Enter Server Details", self.font, self.WHITE, (self.SCREEN_WIDTH // 2, 100))
            self.draw_text("IP Address:", self.small_font, self.WHITE, (self.SCREEN_WIDTH // 2 - 200, 200))
            self.draw_text("Port:", self.small_font, self.WHITE, (self.SCREEN_WIDTH // 2 - 200, 300))

            # Retângulos para entrada de IP e porta
            ip_box = pygame.Rect(self.SCREEN_WIDTH // 2 - 100, 180, 300, 40)
            port_box = pygame.Rect(self.SCREEN_WIDTH // 2 - 100, 280, 300, 40)

            pygame.draw.rect(self.screen, self.BLUE if active_input == "ip" else self.WHITE, ip_box, 2)
            pygame.draw.rect(self.screen, self.BLUE if active_input == "port" else self.WHITE, port_box, 2)

            # Exibir texto digitado
            self.draw_text(ip, self.small_font, self.WHITE, ip_box.center)
            self.draw_text(port, self.small_font, self.WHITE, port_box.center)

            # Botão para confirmar
            confirm_button = pygame.Rect(self.SCREEN_WIDTH // 2 - 100, 350, 200, 50)
            pygame.draw.rect(self.screen, self.WHITE, confirm_button)
            self.draw_text("Confirm", self.small_font, self.BLACK, confirm_button.center)

            # Botão para voltar
            back_button = pygame.Rect(self.SCREEN_WIDTH // 2 - 100, 450, 200, 50)
            pygame.draw.rect(self.screen, self.WHITE, back_button)
            self.draw_text("Back", self.small_font, self.BLACK, back_button.center)

            pygame.display.flip()

    def credits_screen(self):
        """Tela para exibir os créditos do jogo."""
        while True:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    pygame.quit()
                    sys.exit()
                elif event.type == pygame.MOUSEBUTTONDOWN:
                    if event.button == 1:  # Clique esquerdo
                        return  # Voltar ao menu principal

            # Desenhar tela de créditos
            self.screen.fill(self.GRAY)

            # Título
            self.draw_text("Credits", self.font, self.WHITE, (self.SCREEN_WIDTH // 2, 100))

            # Lista de créditos
            credits = [
                "Criadores:",
                "Gabriel Afonso Barbosa",
                "Yury Araujo",
                "Igor Augusto",
                "Michele",
                "Miller",
                "Pedro"
            ]

            for i, credit in enumerate(credits):
                self.draw_text(credit, self.small_font, self.WHITE, (self.SCREEN_WIDTH // 2, 200 + i * 50))

            # Instrução para voltar
            self.draw_text("Click anywhere to return", self.small_font, self.WHITE, (self.SCREEN_WIDTH // 2, self.SCREEN_HEIGHT - 50))

            pygame.display.flip()

# Iniciar menu principal
menu = Menu()
menu.menu_loop()
