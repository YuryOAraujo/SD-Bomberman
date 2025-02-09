import pygame
from player.player import Player

class PlayerManager:

    """
    Gerencia os jogadores em um jogo multiplayer.

    Essa classe é responsável por inicializar os jogadores, atualizar suas posições
    e redefinir seus estados. Ela também coordena a interação entre o jogador local
    e os outros jogadores, com base nos dados recebidos da rede.
    """
        
    def __init__(self, network_client, player_data):

        """
        Inicializa o gerenciador de jogadores.

        Args:
            network_client (NetworkClient): Instância do cliente de rede para comunicação com o servidor.
        """
                
        self.players = pygame.sprite.Group()
        self.local_player = None
        self.network_client = network_client
        self.player_data = player_data

    def initialize_players(self):

        """
        Inicializa os jogadores e define o jogador local com base no ID fornecido pelo servidor.

        Cria instâncias da classe `Player` para até 4 jogadores e posiciona cada jogador
        na posição inicial correspondente. Define o jogador local com base no `player_id`
        do cliente de rede.
        """

        for player_id, player_data in self.player_data.items():
            position = player_data['position']
            name = player_data['name']
            player = Player(player_id, initial_position=position)
            player.round_wins = 0
            player.name = name

            player_data["sprints"] = player.animations
            
            self.players.add(player)

        self.local_player = list(self.players)[self.network_client.player_id - 1]

    def update_players(self):

        """
        Atualiza as posições e direções dos jogadores com base nos dados recebidos da rede.

        Para cada jogador remoto (não local), a posição e a direção são atualizadas
        de acordo com as informações disponíveis em `player_data`.
        """

        for player_id, player_data in self.player_data.items():

            position = player_data['position']
            direction = player_data['direction']
            
            if player_id != self.network_client.player_id:
                player = list(self.players)[player_id - 1]
                player.set_position(position)
                player.direction = direction
                
                player.update()

    def update_player_all(self):

        """
        Atualiza todos os dados dos jogadores com base nas informações da rede.
        """

        for player_id, player_data in self.player_data.items():

            position = player_data['position']
            direction = player_data['direction']
            round_wins = player_data['round_wins']
            
            # Verifica se o nome está presente nos dados do jogador antes de atualizar
            name = player_data.get('name', None)

            player = list(self.players)[player_id - 1]
            player.set_position(position)
            player.direction = direction
            player.round_wins = round_wins
            
            # Se o nome estiver presente, atualiza
            if name is not None:
                player.name = name
            
            player.update()

        
    def reset_players(self):

        """
        Redefine os jogadores para seus estados iniciais.

        Reseta a posição inicial, o estado de eliminação e os dados das bombas de todos os jogadores.
        """
        
        for player in self.players:
            player.eliminated = False
            player.reset_bombs()

    def update_player_data(self):

        """
            Atualiza o dicionário player_data com as informações atuais dos jogadores.

            Percorre todos os jogadores e armazena suas posições e direções no player_data.
        """

        for player in self.players:
            self.player_data[player.player_id] = {
                'position': player.rect.topleft,
                'direction': player.direction,
                'name': player.name,
                'round_wins': player.round_wins
            }

    def eliminate_player(self, player_id: int) -> None:

        """
        Elimina um jogador específico com base no player_id.

        Args:
            player_id (int): ID do jogador a ser eliminado.
        """
        for player in self.players:
            if player.player_id == player_id:
                player.eliminate()
                break

    def apply_power(self, player_id: int, power_id: int) -> None:

        """
        Elimina um jogador específico com base no player_id.

        Args:
            player_id (int): ID do jogador a ser eliminado.
        """
        for player in self.players:
            if player.player_id == player_id:
                player.apply_power(power_id)
                break

    def get_player_by_id(self, player_id: int):

        """
        Retorna um jogador com base no ID fornecido.

        Args:
            player_id (int): O ID do jogador a ser buscado.

        Returns:
            Player: A instância do jogador correspondente ao ID ou None se não for encontrado.
        """
        
        for player in self.players:
            if player.player_id == player_id:
                return player
        return None
