import pygame
import socket
import pickle
from constants import *
from player import Player
from map import Map
from threading import Thread
from bomb import Bomb

from network_client import NetworkClient
from player_manager import PlayerManager
from bomb_manager import BombManager

player_positions = [
    (48, 48),
    (624, 48),
    (48, 624),
    (624, 624)
]

class Game:
    def __init__(self):
        pygame.init()
        self.screen = pygame.display.set_mode((WIDTH, HEIGHT))
        pygame.display.set_caption(TITLE)
        self.clock = pygame.time.Clock()
        self.game_active = True

        self.network_client = NetworkClient('127.0.0.1', 5555)
        self.player_manager = PlayerManager(self.network_client)
        self.bomb_manager = BombManager(self.player_manager.players)
        self.map = None

        self.round_active = False
        self.elapsed_rounds = 0
        self.max_wins = 3
        self.winner = ''
        self.game_over = False

        self.last_position = (0, 0)

        self.connect_to_server()

    def connect_to_server(self):
        if self.network_client.connect():
            self.map = Map(pickle.loads(self.network_client.client.recv(4096)))
            self.player_manager.initialize_players()
            Thread(target=self.listen_for_updates, daemon=True).start()
        else:
            exit()

    def listen_for_updates(self):
        while True:
            data = self.network_client.receive_data()
            if data:
                if isinstance(data, dict) and "type" in data:
                    if data["type"] == "player_data":
                        self.player_manager.player_data = data["players"]
                    elif data["type"] == "bomb":
                        self.bomb_manager.add_bomb(data)
                    elif data["type"] == "grid_update":
                        self.map.grid = data["grid"]
                        self.map.draw_static_map() 

    def send_position_and_direction(self):
        local_player = self.player_manager.local_player
        if abs(local_player.rect.x - self.last_position[0]) > 1 or abs(local_player.rect.y - self.last_position[1]) > 1:
            data = {
                "type": "player_update",
                "position": local_player.rect.topleft,
                "direction": local_player.direction,
            }
            self.network_client.send_data(data)
            self.last_position = local_player.rect.topleft

    def send_bomb(self, bomb):
        data = {
            "type": "bomb",
            "position": bomb.rect.topleft,
            "player_id": bomb.player_id,
            "planted": bomb.planted,
        }
        self.network_client.send_data(data)

    def reset_round(self):
        self.bomb_manager.reset_bombs()
        self.player_manager.reset_players()

    def run(self):

        while self.game_active:

            if not self.game_over:

                print(f'Current round: {self.elapsed_rounds}')
                self.round_active = True
                self.reset_round()

                for player in self.player_manager.players:
                    if player.round_wins == self.max_wins:
                        self.round_active = False
                        self.winner = player.player_id
                        print(f"Player {self.winner} wins the game!")
                        self.game_over = True
                        break

                while self.round_active:
                    
                    self.screen.fill(WHITE)

                    # Desenha o mapa
                    self.map.draw_map(self.screen)

                    for event in pygame.event.get():
                        if event.type == pygame.QUIT:
                            pygame.quit()
                            exit()

                    bomb = self.player_manager.local_player.update(is_local_player=True, obstacles=self.map.obstacles)
                    if bomb:
                        self.bomb_manager.bombs.add(bomb)
                        self.send_bomb(bomb)

                    self.send_position_and_direction()
                    self.player_manager.update_players()

                    last_eliminated_player = self.bomb_manager.update_bombs(self.screen)

                    self.bomb_manager.bombs.draw(self.screen)
                    self.player_manager.players.draw(self.screen)

                    alive_players = [player for player in self.player_manager.players if not player.eliminated]

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