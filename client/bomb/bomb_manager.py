import pygame
from bomb.bomb import Bomb

class BombManager:

    """
    Classe responsável por gerenciar as bombas no jogo, incluindo adicionar novas bombas,
    atualizar o estado das bombas e verificar interações com jogadores.

    Atributos:
        bombs (pygame.sprite.Group): Grupo de objetos de bomba ativos no jogo.
        players (list): Lista de jogadores ativos no jogo.
    """
    
    def __init__(self, players):

        """
        Inicializa o gerenciador de bombas.

        Args:
            players (list): Lista de jogadores que participarão do jogo.
        """

        self.bombs = pygame.sprite.Group()
        self.players = players

    def add_bomb(self, bomb_data):

        """
        Adiciona uma nova bomba ao jogo se ela não existir no mesmo local.

        Args:
            bomb_data (dict): Dados da bomba a ser adicionada. Contém:
                - position (tuple): Coordenadas (x, y) da posição da bomba.
                - player_id (int): ID do jogador que plantou a bomba.
                - planted (float): Tempo em que a bomba foi plantada.
        """

        bomb_position = bomb_data["position"]
        owner_id = bomb_data["player_id"]
        planted_time = bomb_data["planted"]

        # Procura pelo jogador que plantou a bomba
        player = None
        for p in self.players:
            if p.player_id == owner_id:
                player = p
                break

        # Verifica se já existe uma bomba na mesma posição
        for bomb in self.bombs:
            if bomb.rect.topleft == bomb_position:
                return

        # Cria e adiciona a nova bomba
        bomb = Bomb(bomb_position[0], bomb_position[1], owner_id, player)
        bomb.planted = planted_time
        self.bombs.add(bomb)

    def update_bombs(self, screen):

        """
        Atualiza o estado das bombas, verifica explosões e elimina jogadores atingidos.

        Args:
            screen (pygame.Surface): Superfície onde os elementos do jogo são desenhados.

        Returns:
            Player or None: Retorna o último jogador eliminado, se houver, ou None.
        """

        last_eliminated_player = None
        for bomb in self.bombs:

            # Atualiza o estado da bomba (inclui explosões)
            bomb.update(screen)

            # Verifica colisões entre explosões e jogadores
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

        """
        Remove todas as bombas ativas, reiniciando o gerenciador.
        """
        
        self.bombs.empty()
