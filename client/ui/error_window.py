# error_window.py
import pygame

def show_error_window(message):

    """Exibe uma janela de erro com a mensagem fornecida."""

    # Inicializa o Pygame (se ainda não estiver inicializado)
    if not pygame.get_init():
        pygame.init()

    # Configurações da janela de erro
    ERROR_WINDOW_WIDTH = 400
    ERROR_WINDOW_HEIGHT = 300
    ERROR_WINDOW_SIZE = (ERROR_WINDOW_WIDTH, ERROR_WINDOW_HEIGHT)

    # Obtém as dimensões da tela principal
    screen_info = pygame.display.Info()
    screen_width = screen_info.current_w
    screen_height = screen_info.current_h

    # Calcula a posição central da janela de erro
    window_x = (screen_width - ERROR_WINDOW_WIDTH) // 2
    window_y = (screen_height - ERROR_WINDOW_HEIGHT) // 2

    # Define a posição da janela
    error_screen = pygame.display.set_mode(ERROR_WINDOW_SIZE, pygame.NOFRAME)
    pygame.display.set_caption("Erro")

    # Cores
    WHITE = (255, 255, 255)
    BLACK = (0, 0, 0)
    HIGHLIGHT = (255, 200, 0)  
    DARK_OVERLAY = (20, 20, 30)
    BUTTON_COLOR = (0, 150, 200)  
    BUTTON_HOVER_COLOR = (0, 200, 255)  

    # Fonte para o texto
    font = pygame.font.Font(None, 36)

    # Quebra a mensagem em várias linhas, se necessário
    def render_multiline_text(message, font, color):
        words = message.split(' ')
        lines = []
        current_line = ''
        for word in words:
            # Verifica se a palavra cabe na linha atual
            test_line = f'{current_line} {word}' if current_line else word
            test_width, _ = font.size(test_line)
            if test_width <= ERROR_WINDOW_WIDTH - 40:  # 40 pixels de margem
                current_line = test_line
            else:
                # Se não couber, adiciona a linha atual à lista e começa uma nova
                lines.append(current_line)
                current_line = word
        lines.append(current_line)  # Adiciona a última linha
        return lines

    # Renderiza o texto em várias linhas
    lines = render_multiline_text(message, font, BLACK)
    line_height = font.get_linesize()

    # Botão "Fechar"
    button_width = 120  
    button_height = 40  
    button_rect = pygame.Rect(
        (ERROR_WINDOW_WIDTH - button_width) // 2,  
        ERROR_WINDOW_HEIGHT - button_height - 40,  
        button_width,
        button_height
    )

    # Loop principal da janela de erro
    running = True
    while running:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:  # Fecha a janela ao clicar no "X"
                running = False
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_RETURN or event.key == pygame.K_ESCAPE:  # Fecha ao pressionar Enter ou Esc
                    running = False
            elif event.type == pygame.MOUSEBUTTONDOWN:
                if button_rect.collidepoint(event.pos):  # Fecha ao clicar no botão "Fechar"
                    running = False

        # Preenche o fundo da janela
        error_screen.fill(DARK_OVERLAY)

        # Desenha o container da janela de erro
        container_rect = pygame.Rect(20, 20, ERROR_WINDOW_WIDTH - 40, ERROR_WINDOW_HEIGHT - 120)
        pygame.draw.rect(error_screen, (30, 30, 40), container_rect, border_radius=10)
        pygame.draw.rect(error_screen, HIGHLIGHT, container_rect, 2, border_radius=10)

        # Renderiza cada linha do texto
        y_offset = (ERROR_WINDOW_HEIGHT - (len(lines) * line_height)) // 2 - 20  # Centraliza verticalmente
        for line in lines:
            text_surface = font.render(line, True, WHITE)
            text_rect = text_surface.get_rect(center=(ERROR_WINDOW_WIDTH // 2, y_offset))
            error_screen.blit(text_surface, text_rect)
            y_offset += line_height  # Move para a próxima linha

        # Verifica se o mouse está sobre o botão
        mouse_pos = pygame.mouse.get_pos()
        is_hovered = button_rect.collidepoint(mouse_pos)

        # Cor do botão (azul padrão ou azul claro no hover)
        button_color = BUTTON_HOVER_COLOR if is_hovered else BUTTON_COLOR

        # Desenha o botão "Fechar"
        pygame.draw.rect(error_screen, button_color, button_rect, border_radius=10)
        button_text = font.render("Fechar", True, WHITE)
        button_text_rect = button_text.get_rect(center=button_rect.center)
        error_screen.blit(button_text, button_text_rect)

        # Atualiza a tela
        pygame.display.flip()

    # Fecha a janela de erro e restaura a janela principal
    pygame.display.quit()