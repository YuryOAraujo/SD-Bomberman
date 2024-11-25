import pygame
from sys import exit
from constants import *
from player import Player


class Game:
    def __init__(self):
        pygame.init()
        self.screen = pygame.display.set_mode((WIDTH, HEIGHT))
        pygame.display.set_caption(TITLE)
        self.clock = pygame.time.Clock()
        self.game_active = False
        self.player = pygame.sprite.GroupSingle()
        self.player.add(Player(4))
        self.enemies = pygame.sprite.Group()

    def run(self):
        while True:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    pygame.quit()
                    exit()

            self.screen.fill(WHITE)

            self.player.draw(self.screen)
            self.player.update()

            self.enemies.draw(self.screen)
            self.enemies.update()

            pygame.display.update()
            self.clock.tick(FPS)

if __name__ == "__main__":
    game = Game()
    game.run()