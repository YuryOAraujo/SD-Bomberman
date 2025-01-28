import pygame
from bomb import Bomb

class BombManager:
    def __init__(self, players):
        self.bombs = pygame.sprite.Group()
        self.players = players

    def add_bomb(self, bomb_data):
        bomb_position = bomb_data["position"]
        owner_id = bomb_data["player_id"]
        planted_time = bomb_data["planted"]

        player = None
        for p in self.players:
            if p.player_id == owner_id:
                player = p
                break

        for bomb in self.bombs:
            if bomb.rect.topleft == bomb_position:
                return

        bomb = Bomb(bomb_position[0], bomb_position[1], owner_id, player)
        bomb.planted = planted_time
        self.bombs.add(bomb)

    def update_bombs(self, screen):
        last_eliminated_player = None
        for bomb in self.bombs:
            bomb.update(screen)

            if bomb.exploding:
                for player in self.players:
                    if not player.eliminated:
                        for (x, y), explosion_sprite in bomb.explosion_sprites.items():
                            explosion_rect = explosion_sprite.get_rect(topleft=(x, y))
                            if player.rect.colliderect(explosion_rect):
                                player.eliminate()
                                last_eliminated_player = player
                                print(f"Player {player.player_id} has been eliminated!")
        return last_eliminated_player

    def reset_bombs(self):
        self.bombs.empty()