import pygame
import socket
import pickle
from constants import *
from player import Player
from map import Map
from threading import Thread
from menu import Menu
from game_ui import GameUI
import time

player_positions = [
    (48, 48),
    (624, 48),
    (48, 624),
    (624, 624)
]

class Game:
    def __init__(self, ip, port) -> None:
        pygame.init()
        self.screen = pygame.display.set_mode((WIDTH, HEIGHT))
        pygame.display.set_caption(TITLE)
        self.clock = pygame.time.Clock()
        self.game_active = True

        self.players = pygame.sprite.Group()
        self.bombs = pygame.sprite.Group()
        self.local_player = None

        self.client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.server_host = ip  # Use o IP fornecido
        self.server_port = port  # Use a porta fornecida
        self.player_id = None
        self.player_data = []
        self.map = None

        self.round_active = False
        self.elapsed_rounds = 0
        self.max_wins = 3
        self.winner = ''
        self.game_over = False

        # Usar fallback para as imagens dos jogadores
        self.player_images = []
        for i in range(4):
            # Fallback: uma superfície vazia
            fallback_image = pygame.Surface((32, 32))  # Tamanho padrão
            fallback_image.fill((255, 0, 0))  # Preenche com vermelho
            self.player_images.append(fallback_image)

        # Inicializar a interface do usuário
        self.ui = GameUI(
            screen=self.screen,
            players=self.players,  # Passar a lista de jogadores
            ui_width=200,  # Largura da área da interface
            map_width=WIDTH,  # Largura do mapa
            player_images=self.player_images
        )

        self.connect_to_server()

    def connect_to_server(self) -> None:
        try:
            self.client.connect((self.server_host, self.server_port))

            self.player_id = pickle.loads(self.client.recv(1024))
            print(f"Connected to server as Player {self.player_id}")

            self.map = Map(pickle.loads(self.client.recv(4096)))

            for i in range(4):
                player = Player(i + 1, initial_position=player_positions[i])

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

    def reset_round(self) -> None:
        self.bombs.empty()
        
        for player in self.players:
            player.rect.topleft = player_positions[player.player_id - 1]
            player.eliminated = False 
            player.reset_bombs()

    def run(self) -> None:
        while self.game_active:
            if not self.game_over:
                print(f'Current round: {self.elapsed_rounds}')
                self.round_active = True
                self.reset_round()

                for player in self.players:
                    if player.round_wins == self.max_wins:
                        self.round_active = False
                        self.winner = player.player_id
                        print(f"Player {self.winner} wins the game!")
                        self.game_over = True
                        break

                while self.round_active:
                    self.screen.fill(WHITE)
                    for event in pygame.event.get():
                        if event.type == pygame.QUIT:
                            pygame.quit()
                            exit()

                    # Desenhar o mapa sem deslocamento (começa no canto esquerdo)
                    self.map.draw_map(self.screen)

                    # Atualizar e desenhar os jogadores e bombas
                    bomb = self.local_player.update(is_local_player=True, obstacles=self.map.osbtacles)
                    if bomb:
                        self.bombs.add(bomb)

                    self.send_position_and_direction()

                    for i, data in enumerate(self.player_data):
                        if i != self.player_id:
                            player = list(self.players)[i]
                            player.set_position(data["position"])
                            player.direction = data["direction"]
                            player.update()

                    last_eliminated_player = None

                    for bomb in self.bombs:
                        bomb.update(self.screen)

                        if bomb.exploding:
                            for player in self.players:
                                if not player.eliminated:
                                    for (x, y), explosion_sprite in bomb.explosion_sprites.items():
                                        explosion_rect = explosion_sprite.get_rect(topleft=(x, y))
                                        if player.rect.colliderect(explosion_rect):
                                            player.eliminate()
                                            last_eliminated_player = player
                                            print(f"Player {player.player_id} has been eliminated!")

                    self.bombs.draw(self.screen)
                    self.players.draw(self.screen)

                    time_left = 100  # Substitua pelo tempo real do jogo
                    self.ui.draw(time_left)

                    # Verificar se o round terminou
                    alive_players = [player for player in self.players if not player.eliminated]

                    if len(alive_players) <= 1:
                        winner = alive_players[0] if alive_players else last_eliminated_player
                        if winner:
                            winner.round_wins += 1
                            print(f"Player {winner.player_id} wins the round!")
                        self.elapsed_rounds += 1
                        break

                    pygame.display.update()
                    self.clock.tick(FPS)


if __name__ == "__main__":
    Game().run()