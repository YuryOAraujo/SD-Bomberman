import pygame
import socket
import pickle
from constants import *
from player import Player
from map import Map
from threading import Thread
from bomb import Bomb
import time

player_positions = [
    (48, 48),
    (624, 48),
    (48, 624),
    (624, 624)
]

class Game:
    def __init__(self) -> None:
        pygame.init()
        self.screen = pygame.display.set_mode((WIDTH, HEIGHT))
        pygame.display.set_caption(TITLE)
        self.clock = pygame.time.Clock()
        self.game_active = True

        self.players = pygame.sprite.Group()
        self.bombs = pygame.sprite.Group()
        self.local_player = None

        self.client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.server_host = '127.0.0.1'
        self.server_port = 5555
        self.player_id = None
        self.player_data = []
        self.map = None
        self.last_position = (0, 0)

        self.round_active = False
        self.elapsed_rounds = 0
        self.max_wins = 3
        self.winner = ''
        self.game_over = False

        self.connect_to_server()

    def connect_to_server(self) -> None:
        try:
            self.client.connect((self.server_host, self.server_port))

            self.player_id = pickle.loads(self.client.recv(4096))
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
                data = pickle.loads(self.client.recv(4096))
                
                if isinstance(data, dict) and "type" in data:
                    if data["type"] == "bomb":
                        print(f'receive: {data}')
                    if data["type"] == "player_data":
                        self.player_data = data["players"]
                    elif data["type"] == "bomb":
                        self.add_bomb_from_data(data)
                else:
                    print(f"Unexpected data format received: {data}")

            except Exception as e:
                print(f"Connection lost: {e}")
                self.client.close()
                exit()

    def add_bomb_from_data(self, bomb_data):
        bomb_position = bomb_data["position"]
        owner_id = bomb_data["player_id"]
        planted_time = bomb_data["planted"]  # Recebe o tempo de plantação

        player = None
        for p in self.players:
            if p.player_id == owner_id:
                player = p
                break

        #Verifica se a bomba já foi criada
        for bomb in self.bombs:
            if bomb.rect.topleft == bomb_position:
                return

        # Cria uma nova bomba com o tempo de plantação correto
        bomb = Bomb(bomb_position[0], bomb_position[1], owner_id, player)
        bomb.planted = planted_time  # Define o mesmo tempo de plantação enviado pelo servidor
        self.bombs.add(bomb)

    def send_position_and_direction(self) -> None:
        try:
            # Only send position update if player position has changed significantly
            if abs(self.local_player.rect.x - self.last_position[0]) > 1 or abs(self.local_player.rect.y - self.last_position[1]) > 1:
                data = {
                    "type": "player_update",
                    "position": self.local_player.rect.topleft,
                    "direction": self.local_player.direction,
                }
                self.client.send(pickle.dumps(data))
                self.last_position = self.local_player.rect.topleft  # Store the new position
        except Exception as e:
            print(f"Failed to send position: {e}")
            self.client.close()
            exit()

    def send_bomb(self, bomb):
        try:
            data = {
                "type": "bomb",
                "position": bomb.rect.topleft,
                "player_id": bomb.player_id,
                "planted": bomb.planted,  # Adiciona o tempo de plantação
            }
            self.client.send(pickle.dumps(data))
        except Exception as e:
            print(f"Failed to send bomb data: {e}")
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
                        #Retornar para o menu
                        self.game_over = True
                        break            

                while self.round_active:
                    self.screen.fill(WHITE)
                    for event in pygame.event.get():
                        if event.type == pygame.QUIT:
                            pygame.quit()
                            exit()

                    #self.map.draw_map(self.screen)

                    bomb = self.local_player.update(is_local_player=True, obstacles=self.map.obstacles)
                    if bomb:
                        self.bombs.add(bomb)
                        self.send_bomb(bomb)

                    
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
