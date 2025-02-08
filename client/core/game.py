import pygame
import pickle
from config.constants import *
from player.player import Player
from utils.map import Map
from threading import Thread
from bomb.bomb import Bomb
import sys
import random
import math

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
        self.elapsed_rounds = None
        self.max_wins = MAX_WINS
        self.winner = ''
        self.game_over = False

        self.font = pygame.font.Font(None, 36)  # Adiciona a fonte

        self.last_position = (0, 0)

        self.connect_to_server()

    def connect_to_server(self):

        """
        Conecta ao servidor de jogos. Se a conexão for bem-sucedida, inicializa o mapa e
        os jogadores, e inicia uma thread para ouvir atualizações do servidor.
        """
                
        if self.network_client.connect():
            data = pickle.loads(self.network_client.client.recv(4096))
            self.map = Map(*data['map'])
            self.elapsed_rounds = data['round']
            self.player_manager.initialize_players(data['wins'])
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
                        for i, player_data in enumerate(data["players"]):
                            if i < len(self.player_manager.players):
                                player = list(self.player_manager.players)[i]
                                if "name" in player_data:
                                    player.name = player_data["name"]
                    elif data["type"] == DATA_TYPE_BOMB:
                        self.bomb_manager.add_bomb(data)
                    elif data["type"] == DATA_TYPE_GRID_UPDATE:
                        self.map.grid = data["grid"]
                        self.map.draw_static_map()
                    elif data["type"] == "win":
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
                "name": local_player.name,  # Adicionar nome do jogador
                "player_id": local_player.player_id
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

    def send_winner(self, player_id):
        data = {
            "type": "win",
            "player": player_id
        }
        self.network_client.send_data(data)

    def reset_round(self):

        """
        Reinicia o estado do jogo para uma nova rodada, incluindo
        a posição dos jogadores e bombas.
        """

        self.bomb_manager.reset_bombs()
        self.player_manager.reset_players()

    def show_winner_screen(self, winner):
        def create_gradient_background(width, height, start_color, end_color):
            background = pygame.Surface((width, height))
            for y in range(height):
                r = start_color[0] + (end_color[0] - start_color[0]) * y / height
                g = start_color[1] + (end_color[1] - start_color[1]) * y / height
                b = start_color[2] + (end_color[2] - start_color[2]) * y / height
                pygame.draw.line(background, (r, g, b), (0, y), (width, y))
            return background

        class Explosion:
            def __init__(self, x, y):
                self.x = x
                self.y = y
                self.radius = 1
                self.max_radius = random.randint(10, 20)
                self.growth_rate = random.uniform(0.5, 1.5)
                self.alpha = 255
                self.fade_rate = random.uniform(3, 7)
                self.color = (255, random.randint(100, 200), 0)  # Tons de laranja/amarelo
                self.active = True

            def update(self):
                self.radius += self.growth_rate
                self.alpha -= self.fade_rate
                if self.alpha <= 0 or self.radius >= self.max_radius:
                    self.active = False

            def draw(self, surface):
                if self.active:
                    surf = pygame.Surface((self.radius * 2, self.radius * 2), pygame.SRCALPHA)
                    pygame.draw.circle(surf, (*self.color, int(self.alpha)), 
                                    (self.radius, self.radius), self.radius)
                    surface.blit(surf, (self.x - self.radius, self.y - self.radius))

        background = create_gradient_background(self.screen.get_width(), self.screen.get_height(), 
                                            (0, 0, 100), (0, 0, 50))
        
        title_font = pygame.font.Font(None, 72)
        text_font = pygame.font.Font(None, 48)
        
        explosions = []
        clock = pygame.time.Clock()
        start_time = pygame.time.get_ticks()
        
        while True:
            current_time = pygame.time.get_ticks()
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    pygame.quit()
                    sys.exit()
                elif event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_RETURN:
                        return

            # Criar novas explosões aleatoriamente
            if random.random() < 0.1:  # Ajuste este valor para controlar a frequência das explosões
                x = random.randint(0, self.screen.get_width())
                y = random.randint(0, self.screen.get_height())
                explosions.append(Explosion(x, y))

            self.screen.blit(background, (0, 0))

            # Atualizar e desenhar explosões
            explosions = [exp for exp in explosions if exp.active]
            for explosion in explosions:
                explosion.update()
                explosion.draw(self.screen)

            # Mensagem de parabéns com animação
            scale = 1 + 0.1 * math.sin(current_time * 0.005)
            congrats_text = title_font.render("Parabéns!", True, (255, 255, 0))
            congrats_rect = congrats_text.get_rect(center=(self.screen.get_width() // 2, 100))
            scaled_congrats = pygame.transform.scale(congrats_text, 
                                                (int(congrats_rect.width * scale), 
                                                int(congrats_rect.height * scale)))
            scaled_rect = scaled_congrats.get_rect(center=congrats_rect.center)
            self.screen.blit(scaled_congrats, scaled_rect)

            # Nome do vencedor
            name_text = text_font.render(winner.name, True, (255, 255, 255))
            self.screen.blit(name_text, (self.screen.get_width() // 2 - name_text.get_width() // 2, 200))

            # Figura do vencedor ampliada
            if hasattr(winner, 'animations') and "down" in winner.animations:
                winner_sprite = winner.animations["down"][0]
                scaled_sprite = pygame.transform.scale(winner_sprite, (128, 128)).convert_alpha()
                self.screen.blit(scaled_sprite, (self.screen.get_width() // 2 - 64, 250))

            # Instrução para voltar ao menu
            back_text = text_font.render("Pressione ENTER para voltar ao menu", True, (200, 200, 200))
            self.screen.blit(back_text, (self.screen.get_width() // 2 - back_text.get_width() // 2, 450))

            pygame.display.flip()
            clock.tick(60)

    def run(self):
        """
        Loop principal do jogo, que gerencia o estado do jogo, desenha na tela,
        processa eventos e controla o fluxo de rodadas e vitórias.
        """

        # Inicializa a GameUI
        game_ui = GameUI(self.screen, self.player_manager.players, UI_WIDTH, WIDTH, "assets/icons/trophy.png")

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

                    # Desenha a interface na parte direita da tela
                    game_ui.draw()  # Agora não precisa mais passar o tempo

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
                            if winner.round_wins == self.max_wins:
                                self.show_winner_screen(winner)  # Exibe a tela de vitória
                                return  # Volta ao menu
                            self.send_winner(winner.player_id)
                        self.elapsed_rounds += 1
                        break

                    pygame.display.update()
                    self.clock.tick(FPS)