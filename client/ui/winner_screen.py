import pygame
import random
import math
import sys

class Explosion:
            
    def __init__(self, x, y):
        self.x = x
        self.y = y
        self.radius = 1
        self.max_radius = random.randint(10, 20)
        self.growth_rate = random.uniform(0.5, 1.5)
        self.alpha = 255
        self.fade_rate = random.uniform(3, 7)
        self.color = (255, random.randint(100, 200), 0)  # Tons de laranja/amarelo
        self.active = True

    def update(self):
        self.radius += self.growth_rate
        self.alpha -= self.fade_rate
        if self.alpha <= 0 or self.radius >= self.max_radius:
            self.active = False

    def draw(self, surface):
        if self.active:
            surf = pygame.Surface((self.radius * 2, self.radius * 2), pygame.SRCALPHA)
            pygame.draw.circle(surf, (*self.color, int(self.alpha)), 
                            (self.radius, self.radius), self.radius)
            surface.blit(surf, (self.x - self.radius, self.y - self.radius))

def create_gradient_background(width, height, start_color, end_color):

    background = pygame.Surface((width, height))

    for y in range(height):
        r = start_color[0] + (end_color[0] - start_color[0]) * y / height
        g = start_color[1] + (end_color[1] - start_color[1]) * y / height
        b = start_color[2] + (end_color[2] - start_color[2]) * y / height
        pygame.draw.line(background, (r, g, b), (0, y), (width, y))

    return background

class WinnerScreen:

    """Gerencia a tela de vitória."""

    @staticmethod
    def show_winner_screen(self, screen, winner):

        background = create_gradient_background(screen.get_width(), screen.get_height(), (0, 0, 100), (0, 0, 50))
        
        title_font = pygame.font.Font(None, 72)
        text_font = pygame.font.Font(None, 48)
        
        explosions = []
        clock = pygame.time.Clock()
        start_time = pygame.time.get_ticks()
        
        while True:

            current_time = pygame.time.get_ticks()
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    pygame.quit()
                    sys.exit()
                elif event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_RETURN:
                        return

            # Criar novas explosões aleatoriamente
            if random.random() < 0.1:  # Ajuste este valor para controlar a frequência das explosões
                x = random.randint(0, screen.get_width())
                y = random.randint(0, screen.get_height())
                explosions.append(Explosion(x, y))

            screen.blit(background, (0, 0))

            # Atualizar e desenhar explosões
            explosions = [exp for exp in explosions if exp.active]
            for explosion in explosions:
                explosion.update()
                explosion.draw(screen)

            # Mensagem de parabéns com animação
            scale = 1 + 0.1 * math.sin(current_time * 0.005)
            congrats_text = title_font.render("Parabéns!", True, (255, 255, 0))
            congrats_rect = congrats_text.get_rect(center=(screen.get_width() // 2, 100))
            scaled_congrats = pygame.transform.scale(congrats_text, 
                                                (int(congrats_rect.width * scale), 
                                                int(congrats_rect.height * scale)))
            scaled_rect = scaled_congrats.get_rect(center=congrats_rect.center)
            screen.blit(scaled_congrats, scaled_rect)

            # Nome do vencedor
            name_text = text_font.render(winner.name, True, (255, 255, 255))
            screen.blit(name_text, (screen.get_width() // 2 - name_text.get_width() // 2, 200))

            # Figura do vencedor ampliada
            if hasattr(winner, 'animations') and "down" in winner.animations:
                winner_sprite = winner.animations["down"][0]
                scaled_sprite = pygame.transform.scale(winner_sprite, (128, 128)).convert_alpha()
                screen.blit(scaled_sprite, (screen.get_width() // 2 - 64, 250))

            # Instrução para voltar ao menu
            back_text = text_font.render("Pressione ENTER para voltar ao menu", True, (200, 200, 200))
            screen.blit(back_text, (screen.get_width() // 2 - back_text.get_width() // 2, 450))

            pygame.display.flip()
            clock.tick(60)