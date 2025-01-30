import pygame
import pickle
from config.constants import *
from player.player import Player
from utils.map import Map
from threading import Thread
from bomb.bomb import Bomb

from core.network_client import NetworkClient
from player.player_manager import PlayerManager
from bomb.bomb_manager import BombManager
from ui.game_ui import GameUI

player_positions = [
    (48, 48),
    (624, 48),
    (48, 624),
    (624, 624)
]

# Configurações de rede
SERVER_IP = '127.0.0.1'  # IP do servidor
SERVER_PORT = 5555  # Porta do servidor

# Configurações de rodadas
INITIAL_ROUND = 0  # Número inicial de rodadas
MAX_WINS = 3  # Máximo de vitórias para vencer o jogo

# Tipos de dados enviados ao servidor
DATA_TYPE_PLAYER_UPDATE = "player_update"
DATA_TYPE_BOMB = "bomb"
DATA_TYPE_GRID_UPDATE = "grid_update"
DATA_TYPE_PLAYER_DATA = "player_data"

# Dados padrão da bomba
BOMB_DEFAULT_PLANTED = False

class Game:

    """
    Inicializa o jogo, configurando a tela, conexão com o servidor,
    gerenciadores de jogadores e bombas, e outros parâmetros globais.
    """

    def __init__(self, ip=SERVER_IP, port=SERVER_PORT):

        pygame.init()
        self.screen = pygame.display.set_mode((TOTAL_WIDTH, TOTAL_HEIGHT))  # Usa WIDTH e HEIGHT atualizados
        pygame.display.set_caption(TITLE)
        self.clock = pygame.time.Clock()
        self.game_active = True

        # Inicializa o cliente de rede e gerenciadores
        self.network_client = NetworkClient(ip, port)
        self.player_manager = PlayerManager(self.network_client)
        self.bomb_manager = BombManager(self.player_manager.players)
        self.map = None

        self.round_active = BOMB_DEFAULT_PLANTED
        self.elapsed_rounds = INITIAL_ROUND
        self.max_wins = MAX_WINS
        self.winner = ''
        self.game_over = False

        self.last_position = (0, 0)
        self.time_left = 180 

        self.connect_to_server()

    def connect_to_server(self):

        """
        Conecta ao servidor de jogos. Se a conexão for bem-sucedida, inicializa o mapa e
        os jogadores, e inicia uma thread para ouvir atualizações do servidor.
        """
                
        if self.network_client.connect():
            self.map = Map(*pickle.loads(self.network_client.client.recv(4096)))
            self.player_manager.initialize_players()
            Thread(target=self.listen_for_updates, daemon=True).start()
        else:
            exit()

    def listen_for_updates(self):

        """
        Thread dedicada a ouvir atualizações do servidor, como posições de jogadores,
        bombas plantadas e alterações no mapa.
        """

        while True:
            data = self.network_client.receive_data()
            if data:
                if isinstance(data, dict) and "type" in data:
                    if data["type"] == DATA_TYPE_PLAYER_DATA:
                        self.player_manager.player_data = data["players"]
                    elif data["type"] == DATA_TYPE_BOMB:
                        self.bomb_manager.add_bomb(data)
                    elif data["type"] == DATA_TYPE_GRID_UPDATE:
                        self.map.grid = data["grid"]
                        self.map.draw_static_map() 

    def send_position_and_direction(self):

        """
        Envia ao servidor a posição e a direção atual do jogador local
        apenas se houver alterações significativas em sua posição.
        """

        local_player = self.player_manager.local_player
        if abs(local_player.rect.x - self.last_position[0]) > 1 or abs(local_player.rect.y - self.last_position[1]) > 1:
            data = {
                "type": DATA_TYPE_PLAYER_UPDATE,
                "position": local_player.rect.topleft,
                "direction": local_player.direction,
            }
            self.network_client.send_data(data)
            self.last_position = local_player.rect.topleft

    def send_bomb(self, bomb):

        """
        Envia ao servidor os dados de uma bomba plantada pelo jogador local.
        """

        data = {
            "type": DATA_TYPE_BOMB,
            "position": bomb.rect.topleft,
            "player_id": bomb.player_id,
            "planted": bomb.planted,
        }
        self.network_client.send_data(data)

    def reset_round(self):

        """
        Reinicia o estado do jogo para uma nova rodada, incluindo
        a posição dos jogadores e bombas.
        """

        self.bomb_manager.reset_bombs()
        self.player_manager.reset_players()

    def run(self):
        """
        Loop principal do jogo, que gerencia o estado do jogo, desenha na tela,
        processa eventos e controla o fluxo de rodadas e vitórias.
        """

        # Inicializa a GameUI
        game_ui = GameUI(self.screen, self.player_manager.players, UI_WIDTH, WIDTH, "assets/icons/trophy.png")

        # Tempo inicial do jogo
        start_time = pygame.time.get_ticks()  # Tempo inicial em milissegundos

        while self.game_active:
            if not self.game_over:
                # Configura o início de uma nova rodada
                print(f'Current round: {self.elapsed_rounds}')
                self.round_active = True
                self.reset_round()

                # Verifica se algum jogador já venceu o jogo
                for player in self.player_manager.players:
                    if player.round_wins == self.max_wins:
                        self.round_active = False
                        self.winner = player.player_id
                        print(f"Player {self.winner} wins the game!")
                        self.game_over = True
                        break

                while self.round_active:
                    self.screen.fill(WHITE)

                    # Desenha o mapa na parte esquerda da tela
                    self.map.draw_map(self.screen)

                    # Atualiza o tempo restante
                    current_time = pygame.time.get_ticks()  # Tempo atual em milissegundos
                    elapsed_time = (current_time - start_time) // 1000  # Tempo decorrido em segundos
                    self.time_left = max(0, 180 - elapsed_time)  # Atualiza o tempo restante

                    # Desenha a interface na parte direita da tela
                    game_ui.draw(self.time_left)  # Passa o tempo restante

                    # Processa eventos
                    for event in pygame.event.get():
                        if event.type == pygame.QUIT:
                            pygame.quit()
                            return  # Retorna ao menu

                    # Atualiza o jogador local e verifica se uma bomba foi colocada
                    bomb = self.player_manager.local_player.update(is_local_player=True, obstacles=self.map.obstacles)
                    if bomb:
                        self.bomb_manager.bombs.add(bomb)
                        self.send_bomb(bomb)

                    # Envia a posição e direção do jogador local
                    self.send_position_and_direction()

                    # Atualiza os jogadores
                    self.player_manager.update_players()

                    # Atualiza as bombas e verifica se algum jogador foi eliminado
                    last_eliminated_player = self.bomb_manager.update_bombs(self.screen)

                    # Desenha as bombas e os jogadores
                    self.bomb_manager.bombs.draw(self.screen)
                    self.player_manager.players.draw(self.screen)

                    # Verifica se há apenas um jogador vivo
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