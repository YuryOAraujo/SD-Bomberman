import pygame
import socket
import pickle
from constants import *
from player import Player
from threading import Thread

class Game:
    def __init__(self):
        pygame.init()
        self.screen = pygame.display.set_mode((WIDTH, HEIGHT))
        pygame.display.set_caption(TITLE)
        self.clock = pygame.time.Clock()
        self.game_active = False

        self.players = pygame.sprite.Group()
        self.local_player = None

        self.client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.server_host = '127.0.0.1'
        self.server_port = 5555
        self.player_id = None
        self.player_data = []

        self.connect_to_server()

    def connect_to_server(self):
        try:
            self.client.connect((self.server_host, self.server_port))
            self.player_id = pickle.loads(self.client.recv(1024))
            print(f"Connected to server as Player {self.player_id}")
            
            for i in range(4):
                player = Player(i + 1)
                player.rect.topleft = (400, 300)
                self.players.add(player)
            self.local_player = list(self.players)[self.player_id]

            Thread(target=self.listen_for_updates, daemon=True).start()
        except Exception as e:
            print(f"Failed to connect to server: {e}")
            exit()

    def listen_for_updates(self):
        while True:
            try:
                self.player_data = pickle.loads(self.client.recv(1024))
            except Exception as e:
                print(f"Connection lost: {e}")
                self.client.close()
                exit()

    def send_position_and_direction(self):
        try:
            data = {
                "position": self.local_player.rect.topleft,
                "direction": self.local_player.direction,
            }
            self.client.send(pickle.dumps(data))
        except Exception as e:
            print(f"Failed to send position: {e}")
            self.client.close()
            exit()

    def run(self):
        while True:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    pygame.quit()
                    exit()

            self.local_player.update(is_local_player=True)
            self.send_position_and_direction()

            for i, data in enumerate(self.player_data):
                if i != self.player_id:
                    player = list(self.players)[i]
                    player.set_position(data["position"])
                    player.direction = data["direction"]
                    player.update()

            self.screen.fill(WHITE)
            self.players.draw(self.screen)

            pygame.display.update()
            self.clock.tick(FPS)


if __name__ == "__main__":
    Game().run()
