import time
import threading
from core.network_manager import NetworkManager

import pygame
from config.constants import *
from player.player import Player
from utils.map import Map
from threading import Thread
from bomb.bomb import Bomb
import time
import queue

from player.player_manager import PlayerManager
from bomb.bomb_manager import BombManager

from ui.game_ui import GameUI
from ui.waiting_screen import WaitingScreen
from ui.winner_screen import WinnerScreen
from ui.error_window import show_error_window


class Game:

    def __init__(self, ip=SERVER_IP, port=SERVER_PORT, player_name=""):

        self.init_pygame()
        self.init_game_information()
        self.start(ip, port, player_name)

    def init_pygame(self):

        pygame.init()
        self.screen = pygame.display.set_mode((TOTAL_WIDTH, TOTAL_HEIGHT))
        pygame.display.set_caption(TITLE)
        self.clock = pygame.time.Clock()
        self.font = pygame.font.Font(None, 36)

    def init_game_information(self):
        self.game_active = True
        self.round_active = True
        self.max_wins = 3
        self.game_over = False

        self.message_queue = queue.Queue()  
        
    def start(self, ip, port, player_name):

        result = self.connect(ip, port, player_name)

        if (result == None):
            return
        
        print(f"\nConectado com ID: {result["id"]}")

        self.map = Map(*result["map"]) 
        self.player_data = result["players"] 

        self.player_manager = PlayerManager(self.network, self.player_data)
        self.player_manager.initialize_players()
        self.last_position = (0, 0)

        waiting_screen = WaitingScreen(self.screen, self.network)
        self.player_data = waiting_screen.wait_for_game_start(self.player_data)
        if self.player_data == None:
            return  
        
        self.player_manager.player_data = self.player_data
        self.player_manager.update_player_all()
        
        self.bomb_manager = BombManager(self.player_manager.players)

        self.start_game()

    def start_game(self):

        self.network.send_message({"type": MESSAGE_TYPES["START"]})

        self.elapsed_rounds = 1

        listener_thread = threading.Thread(target=self.listener_for_updates, daemon=True)
        listener_thread.start()

        self.run()

    def connect(self, ip, port, player_name):
        
        self.network = NetworkManager(ip, port, player_name)

        """Inicia a conexão e lida com a entrada do usuário."""

        message = self.network.connect()

        message_type = message.get("type")
                
        if message_type == MESSAGE_TYPES["GAME_IN_PROGRESS"]:
            show_error_window("Jogo em progresso, tente mais tarde")
            return None
        elif message_type == MESSAGE_TYPES["FULL"]:
            show_error_window("Servidor cheio. Conexão recusada.")
            return None
        elif message is None:
            show_error_window("Erro ao conectar ao servidor.")
            return None
        
        return message
        
    def run(self):

        self.game_ui = GameUI(self.screen, self.player_manager.players, UI_WIDTH, WIDTH)

        while self.game_active:

            if not self.game_over:

                if (self.process_messages() == False):
                        self.round_active = False
                        self.game_over = True
                        self.game_active = False
                        WinnerScreen.show_winner_screen(self.screen, self.player_manager.get_player_by_id(self.winner))
                        return

                while self.round_active:

                    if (self.process_messages() == False):
                        self.round_active = False
                        self.game_over = True
                        self.game_active = False
                        WinnerScreen.show_winner_screen(self.screen, self.player_manager.get_player_by_id(self.winner))
                        return

                    self.screen.fill(WHITE)
                    self.map.draw_map(self.screen)
                    self.game_ui.draw(self.elapsed_rounds)

                    # Processa eventos
                    for event in pygame.event.get():
                        self.game_ui.handle_event(event)
                        if event.type == pygame.QUIT:
                            self.network.disconnect()
                            return 
                        
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
                    if last_eliminated_player != None and last_eliminated_player == self.player_manager.local_player:
                        self.send_eliminated_player(last_eliminated_player.player_id)
                
                    self.bomb_manager.bombs.draw(self.screen)
                    self.player_manager.players.draw(self.screen)
                    
                    alive_players = [player for player in self.player_manager.players if not player.eliminated]

                    if len(alive_players) <= 1:

                        winner_round = alive_players[0] if alive_players else last_eliminated_player

                        if winner_round and winner_round == self.player_manager.local_player:
                            self.send_winner(winner_round.player_id)
                        
                        self.round_active = False
                        break
                    
                    pygame.display.update()
                    self.clock.tick(FPS)

    def send_position_and_direction(self):

        """
        Envia ao servidor a posição e a direção atual do jogador local
        apenas se houver alterações significativas em sua posição.
        """

        local_player = self.player_manager.local_player

        if abs(local_player.rect.x - self.last_position[0]) > 1 or abs(local_player.rect.y - self.last_position[1]) > 1:

            data = {
                "type": MESSAGE_TYPES["UPDATE"],
                "position": local_player.rect.topleft,
                "direction": local_player.direction,
                "player_id": local_player.player_id
            }
            
            self.network.send_message(data)
            self.last_position = local_player.rect.topleft
    
    def send_bomb(self, bomb):

        """
        Envia ao servidor os dados de uma bomba plantada pelo jogador local.
        """

        data = {
            "type": MESSAGE_TYPES["BOMB"],
            "position": bomb.rect.topleft,
            "player_id": bomb.player_id,
            "planted": bomb.planted,
            "explosion_range": self.player_manager.local_player.explosion_range
        }

        self.network.send_message(data)

    def send_winner(self, player_id):

        data = {
            "type": MESSAGE_TYPES["WIN"],
            "winner_id": player_id
        }

        print("Eu ganhei")

        self.network.send_message(data)
    
    def send_eliminated_player(self, player_id):

        data = {
            "type": MESSAGE_TYPES["ELIMINATED"],
            "player_id": player_id
        }

        self.network.send_message(data)

    def process_messages(self):

        """Processa mensagens armazenadas na fila."""

        while not self.message_queue.empty():
            
            message = self.message_queue.get() 
            message_type = message.get("type")
            
            if message_type == MESSAGE_TYPES["DISCONNECTED"]:
                self.player_manager.eliminate_player(message["player_id"])

            elif message_type == MESSAGE_TYPES["UPDATE"]:
                self.player_manager.player_data = message["players"]

            elif message_type == MESSAGE_TYPES["BOMB"]:
                self.bomb_manager.add_bomb(message)

            elif message_type == MESSAGE_TYPES["GRID_UPDATE"]:
                self.update_map(message)

            elif message_type == MESSAGE_TYPES["ELIMINATED"]:
                self.player_manager.eliminate_player(message["player_id"])

            elif message_type== MESSAGE_TYPES["UPDATE_POWER"]:
                self.player_manager.apply_power(message["player_id"], message["power"])
                self.update_map(message)

            elif message_type == MESSAGE_TYPES["ROUND_RESET"]:
                self.reset_round(message)

            elif message_type == MESSAGE_TYPES["GAME_OVER"]:
                self.elapsed_rounds = message["round"]
                self.player_manager.player_data = message["players"]
                self.game_ui.update_players_data(self.player_manager.players)
                self.winner = message["winner_id"]
                return False
        
        return True

    def listener_for_updates(self):
        
        while self.game_active:

            message = self.network.receive_messages()
            if message:
                self.message_queue.put(message)

    def update_map(self, message):
        self.map.grid = message["grid"]
        self.map.draw_static_map()

    def reset_round(self, message):

        """
        Reinicia o estado do jogo para uma nova rodada, incluindo
        a posição dos jogadores e bombas.
        """

        self.elapsed_rounds = message["round"]
        print(f'Current round: {self.elapsed_rounds}')
        self.round_active = True
        self.player_manager.player_data = message["players"]  
        self.map.grid = message["grid"]


        self.bomb_manager.reset_bombs()
        self.player_manager.reset_players()

        # Atualiza a UI com os novos jogadores
        self.player_manager.update_player_all()
        self.game_ui.update_players_data(self.player_manager.players)
        self.last_position = (0, 0)

        self.map.draw_static_map() 