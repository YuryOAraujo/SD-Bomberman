import pygame
from player.player import Player

player_positions = [
    (48, 48),
    (624, 48),
    (48, 624),
    (624, 624)
]

class PlayerManager:
    def __init__(self, network_client):
        self.players = pygame.sprite.Group()
        self.local_player = None
        self.network_client = network_client
        self.player_data = []

    def initialize_players(self):
        for i in range(4):
            player = Player(i + 1, initial_position=player_positions[i])
            self.players.add(player)
        self.local_player = list(self.players)[self.network_client.player_id]

    def update_players(self):
        for i, data in enumerate(self.player_data):
            if i != self.network_client.player_id:
                player = list(self.players)[i]
                player.set_position(data["position"])
                player.direction = data["direction"]
                player.update()

    def reset_players(self):
        for player in self.players:
            player.rect.topleft = player_positions[player.player_id - 1]
            player.eliminated = False
            player.reset_bombs()