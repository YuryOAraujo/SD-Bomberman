import pygame
import socket
import pickle
from constants import *
from player import Player
from map import Map
from threading import Thread
from menu import Menu
from game_ui import GameUI 

player_positions = [
    (48, 48),
    (624, 48),
    (48, 624),
    (624, 624)
]

class Game:
    def __init__(self, server_host, server_port) -> None:
        pygame.init()
        self.screen = pygame.display.set_mode((TOTAL_WIDTH, HEIGHT))  # Tela com área da interface
        pygame.display.set_caption(TITLE)
        self.clock = pygame.time.Clock()
        self.game_active = False

        self.players = pygame.sprite.Group()
        self.local_player = None

        self.client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.server_host = server_host  
        self.server_port = server_port 
        self.player_id = None
        self.player_data = []
        self.map = None

        # Conecta ao servidor e inicializa os jogadores
        self.connect_to_server()

        # Obtém as imagens dos personagens virados para frente
        player_images = [player.animations["down"][0] for player in self.players]

        # Inicializa a interface do usuário (UI)
        self.ui = GameUI(self.screen, self.players, UI_WIDTH, WIDTH, player_images)  # Passa as imagens dos personagens

    def connect_to_server(self) -> None:
        try:
            self.client.connect((self.server_host, self.server_port))

            self.player_id = pickle.loads(self.client.recv(1024))
            print(f"Connected to server as Player {self.player_id}")

            self.map = Map(pickle.loads(self.client.recv(4096)))

            for i in range(4):
                player = Player(i + 1)
                player.rect.topleft = player_positions[i]
                self.players.add(player)
            self.local_player = list(self.players)[self.player_id]

            Thread(target=self.listen_for_updates, daemon=True).start()
        except Exception as e:
            print(f"Failed to connect to server: {e}")
            exit()

    def listen_for_updates(self) -> None:
        while True:
            try:
                self.player_data = pickle.loads(self.client.recv(1024))
            except Exception as e:
                print(f"Connection lost: {e}")
                self.client.close()
                exit()

    def send_position_and_direction(self) -> None:
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

    def run(self) -> None:
        time_left = 90  # Exemplo de tempo restante
        while True:
            self.screen.fill(PINK)
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    pygame.quit()
                    exit()

            # Desenha o mapa na área do mapa (à esquerda)
            self.map.draw_map(self.screen)

            self.local_player.update(is_local_player=True, obstacles=self.map.osbtacles)
            self.send_position_and_direction()

            for i, data in enumerate(self.player_data):
                if i != self.player_id:  # Ignora o jogador local
                    player = list(self.players)[i]
                    player.set_position(data["position"])
                    player.direction = data["direction"]
                    player.update()

            self.players.draw(self.screen)

            # Desenha a interface na área da interface (à direita)
            self.ui.draw(time_left)

            pygame.display.update()
            self.clock.tick(FPS)


if __name__ == "__main__":
    Menu().menu_loop()
    
