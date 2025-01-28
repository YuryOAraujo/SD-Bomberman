import pygame
import time
from constants import *
from spritesheet import SpriteSheet
from math import floor

class Bomb(pygame.sprite.Sprite):

    def __init__(self, x, y, player_id, player=None, timer=1, grid_size=(SPRITE_WIDTH * SCALE, SPRITE_HEIGHT * SCALE)):

        super().__init__()
        self.player_id = player_id
        self.player = player
        self.timer = timer
        self.explosion_range = player.explosion_range
        self.planted = time.time()
        self.animations = self.load_bomb_assets()
        self.animation_speed = 0.15
        self.frame_index = 0
        self.grid_size = grid_size

        # Centraliza a posição na célula correta
        self.x, self.y = self.align_to_grid(x, y)
        self.image = self.animations["bomb"][0]
        self.rect = self.image.get_rect(topleft=(self.x, self.y))
        self.exploding = False
        self.explosion_sprites = {}
        self.explosion_alpha = 0
        self.flicker_speed = 10
        self.flicker_timer = 0
    
    def align_to_grid(self, x, y):

        """
        Ajusta as coordenadas (x, y) para o centro da célula da matriz mais próxima,
        garantindo que a bomba seja colocada dentro dos limites da área jogável.
        """
        cell_width, cell_height = self.grid_size

        # Calcula o índice da célula mais próxima
        grid_x = round(x / cell_width) * cell_width
        grid_y = round(y / cell_height) * cell_height

        # Garante que as coordenadas finais estejam dentro dos limites da área jogável
        grid_x = max(0, min(grid_x, PLAYABLE_AREA + cell_width))
        grid_y = max(0, min(grid_y, PLAYABLE_AREA + cell_height))

        return grid_x, grid_y

    def load_bomb_assets(self) -> dict:

        """
        Carrega os sprites da bomba e das explosões.
        """

        sprite_sheet = SpriteSheet(pygame.image.load("client/graphics/bomb_party_v3.png").convert_alpha())
        return {
            "bomb": [
                sprite_sheet.get_image(12, 2, SPRITE_WIDTH, SPRITE_HEIGHT, SCALE, PINK),
                sprite_sheet.get_image(12, 3, SPRITE_WIDTH, SPRITE_HEIGHT, SCALE, PINK),
                sprite_sheet.get_image(12, 4, SPRITE_WIDTH, SPRITE_HEIGHT, SCALE, PINK),
            ],
            "explosion_fade": [
                sprite_sheet.get_image(2, 5, SPRITE_WIDTH, SPRITE_HEIGHT, SCALE, PINK),
                sprite_sheet.get_image(15, 5, SPRITE_WIDTH, SPRITE_HEIGHT, SCALE, PINK),
                sprite_sheet.get_image(15, 4, SPRITE_WIDTH, SPRITE_HEIGHT, SCALE, PINK),
                sprite_sheet.get_image(15, 3, SPRITE_WIDTH, SPRITE_HEIGHT, SCALE, PINK),
            ],
            "explosion_path": [
                sprite_sheet.get_image(0, 5, SPRITE_WIDTH, SPRITE_HEIGHT, SCALE, PINK),
                sprite_sheet.get_image(1, 5, SPRITE_WIDTH, SPRITE_HEIGHT, SCALE, PINK),
                sprite_sheet.get_image(3, 5, SPRITE_WIDTH, SPRITE_HEIGHT, SCALE, PINK),
                sprite_sheet.get_image(15, 0, SPRITE_WIDTH, SPRITE_HEIGHT, SCALE, PINK),
                sprite_sheet.get_image(15, 1, SPRITE_WIDTH, SPRITE_HEIGHT, SCALE, PINK),
                sprite_sheet.get_image(15, 2, SPRITE_WIDTH, SPRITE_HEIGHT, SCALE, PINK),
            ],
        }

    def should_explode(self) -> bool:

        """
        Verifica se a bomba deve explodir com base no tempo de plantio.
        """

        return time.time() - self.planted >= self.timer

    def calculate_explosion_path(self):

        """
        Calcula o caminho da explosão a partir do centro da bomba.
        """

        directions = {
            "left": (-1, 0),
            "right": (1, 0),
            "up": (0, -1),
            "down": (0, 1),
        }
        explosion_tiles = [((self.x, self.y), "center")]

        for direction, (dx, dy) in directions.items():
            for step in range(1, self.explosion_range + 1):
                x = self.x + dx * (SPRITE_WIDTH * SCALE) * step
                y = self.y + dy * (SPRITE_HEIGHT * SCALE) * step

                if not self.valid_tile(x, y):
                    break

                if step == self.explosion_range:
                    explosion_tiles.append(((x, y), direction))
                else:
                    explosion_tiles.append(((x, y), "path"))

        return explosion_tiles

    def valid_tile(self, x, y):

        """
        Verifica se a posição está dentro do limite da área jogável.
        """

        return 0 <= x < PLAYABLE_AREA and 0 <= y < PLAYABLE_AREA

    def explode(self):

        """
        Executa a explosão da bomba, calculando o caminho e animando os sprites.
        """

        self.exploding = True
        self.frame_index = 1

        explosion_tiles = self.calculate_explosion_path()
        self.explosion_sprites = {}

        for (x, y), direction in explosion_tiles:
            sprite = self.get_explosion_sprite(direction, x, y)
            sprite.set_alpha(0)
            self.explosion_sprites[(x, y)] = sprite

    def get_explosion_sprite(self, direction, x, y):

        """
        Retorna o sprite correto para a explosão com base na direção e posição.
        """

        if direction == "center":
            return self.animations["explosion_fade"][0].copy()
        elif direction == "left":
            return self.animations["explosion_path"][0].copy()
        elif direction == "right":
            return self.animations["explosion_path"][2].copy()
        elif direction == "up":
            return self.animations["explosion_path"][3].copy()
        elif direction == "down":
            return self.animations["explosion_path"][5].copy()
        else:
            if x != self.x:
                return self.animations["explosion_path"][1].copy()
            elif y != self.y:
                return self.animations["explosion_path"][4].copy()

    def update_bomb_animation(self):

        """
        Atualiza a animação da bomba antes da explosão.
        """

        self.frame_index += self.animation_speed
        if self.frame_index >= len(self.animations["bomb"]):
            self.frame_index = 0

        self.image = self.animations["bomb"][int(self.frame_index)]

    def update_explosion_animation(self, surface):

        """
        Atualiza a animação da explosão e desenha os sprites na tela.
        """

        self.flicker_timer += 1
        if self.flicker_timer >= self.flicker_speed:
            self.flicker_timer = 0
            self.explosion_alpha = 0 if self.explosion_alpha == 255 else 255

        self.image.set_alpha(self.explosion_alpha)
        surface.blit(self.image, self.rect.topleft)

        for (x, y), sprite in self.explosion_sprites.items():
            sprite.set_alpha(self.explosion_alpha)
            surface.blit(sprite, (x, y))

    def check_explosion_end(self):

        """
        Verifica se a explosão terminou e remove a bomba.
        """

        if time.time() - self.planted >= self.timer + 1:
            self.player.bombs_placed -= 1
            self.kill()

    def update(self, surface):

        """
        Atualiza a animação da bomba ou da explosão.
        """

        if not self.exploding:
            self.update_bomb_animation()

            if self.should_explode():
                self.image = self.animations["explosion_fade"][0]
                self.explode()
        else:
            self.update_explosion_animation(surface)
            self.check_explosion_end()