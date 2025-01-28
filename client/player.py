import pygame
from constants import *
from spritesheet import SpriteSheet
from bomb import Bomb

class Player(pygame.sprite.Sprite):

    def __init__(self, player_id: int, initial_position) -> None:

        """
        Inicializa o jogador com um ID único e uma posição inicial.
        """

        super().__init__()
        self.player_id = player_id

        # Carrega as animações do jogador
        self.animations = self.load_animations()  

        # Direção inicial do jogador
        self.direction = "down"  
        self.image = self.animations[self.direction][0] 
        self.rect = self.image.get_rect() 
        self.rect.topleft = initial_position 
        self.speed = 4  
        self.frame_index = 1  
        self.animation_speed = 0.15 
        self.moving = False 

        # Atributos relacionados a bombas
        self.bombs_placed = 0
        self.max_bombs = 1
        self.explosion_range = 2

        # Estado do jogador
        self.eliminated = False
        self.round_wins = 0

    def load_animations(self) -> dict:

        """
        Carrega as animações do jogador a partir de uma spritesheet.
        """

        sprite_sheet = SpriteSheet(pygame.image.load("client/graphics/bomb_party_v3.png").convert_alpha())
        animations = {
            "down": [],
            "up": [],
            "left": [],
            "right": []
        }

        # Carrega as imagens da spritesheet
        images = []
        for num in range(PLAYER_ANIMATION_LENGTH):
            images.append(sprite_sheet.get_image(num, self.player_id, SPRITE_WIDTH, SPRITE_HEIGHT, SCALE, PINK))

        # Define as animações para cada direção
        animations["down"] = images[1:4]
        animations["up"] = [images[0], images[8], images[9]]
        animations["right"] = images[4:8]
        animations["left"] = [pygame.transform.flip(image, True, False).convert_alpha() for image in images[4:8]]

        return animations

    def place_bomb(self) -> Bomb:

        """
        Coloca uma bomba na posição atual do jogador, se possível.
        """

        if self.bombs_placed < self.max_bombs:
            bomb = Bomb(self.rect.x, self.rect.y, self.player_id, self)
            self.bombs_placed += 1
            return bomb
        return None

    def align_to_grid(self) -> None:

        """
        Alinha o jogador ao grid mais próximo, facilitando o movimento e a colocação de bombas.
        """

        cell_width = SCALE * SPRITE_WIDTH
        cell_height = SCALE * SPRITE_HEIGHT

        offset_x = self.rect.x % cell_width
        offset_y = self.rect.y % cell_height

        if offset_x <= PIXEL_EDGE or offset_x >= cell_width - PIXEL_EDGE:
            self.rect.x = round(self.rect.x / cell_width) * cell_width
        if offset_y <= PIXEL_EDGE or offset_y >= cell_height - PIXEL_EDGE:
            self.rect.y = round(self.rect.y / cell_height) * cell_height

    def handle_movement(self, keys) -> None:

        """
        Processa a entrada do usuário para mover o jogador.
        """

        self.moving = False

        if (keys[pygame.K_LEFT] or keys[pygame.K_a]) and self.rect.left > 0:
            self.rect.x -= self.speed
            self.direction = "left"
            self.moving = True
        elif (keys[pygame.K_RIGHT] or keys[pygame.K_d]) and self.rect.right < WIDTH:
            self.rect.x += self.speed
            self.direction = "right"
            self.moving = True
        elif (keys[pygame.K_UP] or keys[pygame.K_w]) and self.rect.top > 0:
            self.rect.y -= self.speed
            self.direction = "up"
            self.moving = True
        elif (keys[pygame.K_DOWN] or keys[pygame.K_s]) and self.rect.bottom < HEIGHT:
            self.rect.y += self.speed
            self.direction = "down"
            self.moving = True

    def handle_collision(self, obstacles) -> None:

        """
        Verifica e resolve colisões com obstáculos.
        """

        if obstacles is None:
            return

        for row in obstacles:
            for obstacle in row:
                if obstacle is not None and self.rect.colliderect(obstacle):
                    if self.direction == "left":
                        self.rect.left = obstacle.right
                    elif self.direction == "right":
                        self.rect.right = obstacle.left
                    elif self.direction == "up":
                        self.rect.top = obstacle.bottom
                    elif self.direction == "down":
                        self.rect.bottom = obstacle.top

    def player_input(self, obstacles=None) -> Bomb:

        """
        Processa a entrada do jogador, incluindo movimento e colocação de bombas.
        """

        keys = pygame.key.get_pressed()
        prev_direction = self.direction

        self.handle_movement(keys)

        if self.direction != prev_direction:
            self.align_to_grid()

        self.handle_collision(obstacles)

        # Limita o jogador dentro da tela
        self.rect.x = max(0, min(self.rect.x, WIDTH - SPRITE_WIDTH))
        self.rect.y = max(0, min(self.rect.y, HEIGHT - SPRITE_HEIGHT))

        # Coloca uma bomba se a tecla de espaço for pressionada
        if keys[pygame.K_SPACE]:
            bomb = self.place_bomb()
            if bomb:
                return bomb
        return None

    def update_animation(self) -> None:

        """
        Atualiza a animação do jogador com base no estado de movimento.
        """

        if self.moving:
            self.frame_index += self.animation_speed
            if self.frame_index >= len(self.animations[self.direction]):
                self.frame_index = 1
            self.image = self.animations[self.direction][int(self.frame_index)]
        else:
            self.image = self.animations[self.direction][0]

    def set_position(self, new_position) -> None:
        
        """
        Define a posição do jogador e atualiza o estado de movimento.
        """

        if self.rect.topleft != new_position:
            self.moving = True
        else:
            self.moving = False
        self.rect.topleft = new_position

    def update(self, is_local_player: bool = False, obstacles=None) -> Bomb:

        """
        Atualiza o estado do jogador, incluindo entrada, animação e colisões.
        """

        if is_local_player:
            bomb = self.player_input(obstacles)
            if bomb:
                return bomb
        self.update_animation()
        return None

    def reset_bombs(self) -> None:

        """
        Reseta o contador de bombas colocadas.
        """

        self.bombs_placed = 0

    def eliminate(self) -> None:

        """
        Marca o jogador como eliminado e para o movimento.
        """

        self.eliminated = True
        self.moving = False