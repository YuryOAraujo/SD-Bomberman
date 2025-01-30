import pygame
import sys
from ui.menu import Menu

def main():
    # Inicializa o Pygame
    pygame.init()

    # Cria uma instância do menu
    menu = Menu()

    # Inicia o loop do menu
    menu.menu_loop()

if __name__ == "__main__":
    main()