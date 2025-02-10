import pygame
import sys

class MapSelectionScreen:

    def __init__(self, screen, network):

        self.screen = screen
        self.clock = pygame.time.Clock()
        self.font = pygame.font.Font(None, 48)
        self.small_font = pygame.font.Font(None, 36)
        self.HIGHLIGHT = (255, 200, 0)
        self.WHITE = (255, 255, 255)
        self.selected_map = "Mapa1"
        self.running = True
        self.network = network
        
    def draw(self):

        """Desenha a tela de seleção de mapas."""
        
        screen_width, screen_height = self.screen.get_size()
        self.screen.fill((30, 30, 40))
        
        # Container central
        container_rect = pygame.Rect(screen_width // 2 - 300, 100, 600, 400)
        pygame.draw.rect(self.screen, (40, 40, 50), container_rect, border_radius=15)
        pygame.draw.rect(self.screen, self.HIGHLIGHT, container_rect, 2, border_radius=15)
        
        # Título
        title_text = self.font.render("Selecione o Mapa", True, self.HIGHLIGHT)
        self.screen.blit(title_text, (screen_width // 2 - title_text.get_width() // 2, 120))
        
        # Opções de mapa
        map_options = ["Mapa1", "Mapa2"]
        map_rects = []
        for i, option in enumerate(map_options):
            option_rect = pygame.Rect(screen_width // 2 - 100, 200 + i * 80, 200, 50)
            map_rects.append(option_rect)
            
            # Cor do fundo (diferente se selecionado)
            color = (60, 60, 70) if option == self.selected_map else (40, 40, 50)
            pygame.draw.rect(self.screen, color, option_rect, border_radius=8)
            pygame.draw.rect(self.screen, self.HIGHLIGHT, option_rect, 2, border_radius=8)
            
            # Texto da opção
            text_surf = self.small_font.render(option, True, self.WHITE)
            text_rect = text_surf.get_rect(center=option_rect.center)
            self.screen.blit(text_surf, text_rect)
        
        # Botão "Continuar"
        continue_button = pygame.Rect(screen_width // 2 - 100, 400, 200, 50)
        pygame.draw.rect(self.screen, (40, 40, 50), continue_button, border_radius=8)
        pygame.draw.rect(self.screen, self.HIGHLIGHT, continue_button, 2, border_radius=8)
        
        # Texto do botão
        continue_text = self.small_font.render("Continuar", True, self.WHITE)
        continue_rect = continue_text.get_rect(center=continue_button.center)
        self.screen.blit(continue_text, continue_rect)
        
        # Efeito de hover no botão "Continuar"
        if continue_button.collidepoint(pygame.mouse.get_pos()):
            pygame.draw.rect(self.screen, (60, 60, 70), continue_button, border_radius=8)
            self.screen.blit(continue_text, continue_rect)
        
        pygame.display.flip()
        return map_rects, continue_button
    
    def run(self):

        """Executa a tela de seleção de mapas."""
        
        while self.running:
            map_rects, continue_button = self.draw()
            
            for event in pygame.event.get():

                if event.type == pygame.QUIT:
                    self.running = False
                    return None
                  
                elif event.type == pygame.MOUSEBUTTONDOWN:
                    for i, rect in enumerate(map_rects):
                        if rect.collidepoint(event.pos):
                            self.selected_map = ["Mapa1", "Mapa2"][i]

                    if continue_button.collidepoint(event.pos):
                        self.running = False
                        return self.selected_map
                    
                elif event.type == pygame.KEYDOWN:

                    if event.key == pygame.K_UP:
                        self.selected_map = "Mapa1"
                    elif event.key == pygame.K_DOWN:
                        self.selected_map = "Mapa2"
                    elif event.key == pygame.K_RETURN:
                        self.running = False
                        return self.selected_map

            players = self.network.get_state()

            if all(player["connected"] for player in players.values()):
                return "Random"

            self.clock.tick(30)