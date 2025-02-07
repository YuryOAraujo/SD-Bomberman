import pygame
from player.player import Player

player_positions = [
    (48, 48),
    (624, 48),
    (48, 624),
    (624, 624)
]

class PlayerManager:

    """
    Gerencia os jogadores em um jogo multiplayer.

    Essa classe é responsável por inicializar os jogadores, atualizar suas posições
    e redefinir seus estados. Ela também coordena a interação entre o jogador local
    e os outros jogadores, com base nos dados recebidos da rede.
    """
        
    def __init__(self, network_client):

        """
        Inicializa o gerenciador de jogadores.

        Args:
            network_client (NetworkClient): Instância do cliente de rede para comunicação com o servidor.
        """
                
        self.players = pygame.sprite.Group()
        self.local_player = None
        self.network_client = network_client
        self.player_data = []

    def initialize_players(self, wins):

        """
        Inicializa os jogadores e define o jogador local com base no ID fornecido pelo servidor.

        Cria instâncias da classe `Player` para até 4 jogadores e posiciona cada jogador
        na posição inicial correspondente. Define o jogador local com base no `player_id`
        do cliente de rede.
        """
        for i in range(4):
            player = Player(i + 1, initial_position=player_positions[i])
            player.round_wins = wins[player.player_id - 1]
            self.players.add(player)
        self.local_player = list(self.players)[self.network_client.player_id]

    def update_players(self):

        """
        Atualiza as posições e direções dos jogadores com base nos dados recebidos da rede.

        Para cada jogador remoto (não local), a posição e a direção são atualizadas
        de acordo com as informações disponíveis em `player_data`.
        """

        for i, data in enumerate(self.player_data):
            if i != self.network_client.player_id:
                player = list(self.players)[i]
                player.set_position(data["position"])
                player.direction = data["direction"]
                player.update()

    def reset_players(self):

        """
        Redefine os jogadores para seus estados iniciais.

        Reseta a posição inicial, o estado de eliminação e os dados das bombas de todos os jogadores.
        """
        
        for player in self.players:
            player.rect.topleft = player_positions[player.player_id - 1]
            player.eliminated = False
            player.reset_bombs()
    
    def update_players_wins(self, wins):
        for player in self.players:
            player.round_wins = wins[player.player_id - 1]