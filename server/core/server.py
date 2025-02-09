import json
import random
import time

from core.network_server import NetworkServer
from map.map_manager import MapManager
from config.constants import *

import threading

class Server:

    """Gerencia as mensagens e interações dos clientes."""

    def __init__(self):

        self.network = NetworkServer()
        self.current_round = 1
        self.max_wins = 3
        self.player_wins = [0] * self.network.max_clients
        self.player_data = {}
        self.player_states = {}

        self.bombs = []  

        self.lock = threading.Lock() 

        self.map_manager = MapManager(random.choice(STAGES))

        self.game_in_progress = False 

    def start_game(self):

        """Inicia o jogo e impede novas conexões."""

        with self.lock:
            self.game_in_progress = True

    def start(self):

        """Inicia o servidor e escuta mensagens dos clientes."""

        self.network.start_listening(self.process_message)

    def process_message(self, message, addr):

        try:

            if message is None:
                return

            data = message  
            
            msg_type = data.get("type")

            if msg_type == MESSAGE_TYPES["CONNECT"]:
                self.handle_connect(data, addr)
            elif msg_type == MESSAGE_TYPES["GET_STATE"]:
                self.handle_game_state(data, addr)
            elif msg_type == MESSAGE_TYPES["START"]:
                self.start_game()
            elif msg_type == MESSAGE_TYPES["DISCONNECTED"]:
                self.handle_disconnect(addr)
            elif msg_type == MESSAGE_TYPES["UPDATE"]:
                self.handle_update(data, addr)
            elif msg_type == MESSAGE_TYPES["WIN"]:
                self.handle_win(data, addr)
            elif msg_type == MESSAGE_TYPES["BOMB"]:
                self.handle_bomb(data, addr)
            elif msg_type == MESSAGE_TYPES["ELIMINATED"]:
                self.handle_eliminated(data, addr)
            else:
                print("Não reconhecida")

        except json.JSONDecodeError:
            print("Erro ao decodificar dados.")

    def get_game_state(self):
        return  {
                    pid: {
                        "position": self.player_data[pid]["position"] if pid in self.player_data else PLAYER_POSITIONS[(pid - 1) % len(PLAYER_POSITIONS)],
                        "direction": self.player_data.get(pid, {}).get("direction", "down"),
                        "connected": pid in self.network.clients,
                        "name": self.player_data.get(pid, {}).get("name", f"P{pid}"),
                        "round_wins": self.player_wins[pid - 1] 
                    }

                    for pid in range(1, self.network.max_clients + 1)
                }

    def handle_connect(self, data, addr):

        with self.lock:  

            if self.game_in_progress:
                print("Tentativa de conexão recusada: jogo em andamento.")
                response = {"type": MESSAGE_TYPES["GAME_IN_PROGRESS"]}
                self.network.send_message(response, addr)

                return

            """Gerencia novas conexões de clientes."""

            client_id = self.network.register_client(addr)

            if client_id is not None:

                print(f"Cliente {client_id} conectado: {addr}")
                
                # Se não houver nome, atribui um padrão "P{client_id}"
                player_name = data.get("name", f"P{client_id}") 

                # Define posição inicial do novo jogador
                initial_position = PLAYER_POSITIONS[(client_id - 1) % len(PLAYER_POSITIONS)]
                
                # Atualiza o estado interno do jogador
                self.player_data[client_id] = {
                    "position": initial_position,
                    "direction": "down", 
                    "name": player_name,
                    "round_wins": self.player_wins[client_id - 1]
                }

                self.player_states = self.get_game_state()

                # Monta a resposta com ID, estados dos jogadores e informações do mapa
                response = {
                    "type": MESSAGE_TYPES["CONNECT"],
                    "id": client_id,
                    "players": self.player_states,
                    "map": (self.map_manager.get_grid(), self.map_manager.get_stage())
                }

                self.network.send_message(response, addr)
            else:
                print("Número máximo de clientes atingido. Conexão recusada.")
                response = {"type": MESSAGE_TYPES["FULL"]}
                self.network.send_message(response, addr)

    def handle_game_state(self, data, addr):

        with self.lock: 
            self.player_states = self.get_game_state()

        response = {
            "type": MESSAGE_TYPES["GET_STATE"],
            "players": self.player_states
        }

        self.network.send_message(response, addr)

    def handle_disconnect(self, addr):

        """Gerencia a desconexão de clientes."""
        
        client_id = self.network.unregister_client(addr)

        if client_id is not None:
            print(f"Cliente {client_id} desconectado: {addr}")
            response = {
                "type": MESSAGE_TYPES["DISCONNECTED"],
                "player_id": client_id
            }
            
            self.network.broadcast(response, addr)

        # Verifica se restou apenas um jogador
        with self.lock:
            remaining_players = list(self.network.clients.keys())
            
            if len(remaining_players) == 1:
                winner_id = remaining_players[0]
                self._reset_game_all(addr, winner_id)
                
                
    def handle_update(self, data, addr):

        """Atualiza os outros clientes sobre a posição, direção e nome do jogador."""

        player_id = data["player_id"]

        if player_id is not None:

            position = data["position"]


            self.player_data[player_id] = {
                "position": position,
                "direction": data["direction"],
            }

            update_message = {
                "type": MESSAGE_TYPES["UPDATE"],
                "players": self.player_data,
                "grid": self.map_manager.get_grid()
            }

            self.network.broadcast(update_message, addr)
        
        self.handle_power(position, player_id, addr)

    def handle_power(self, position, player_id, addr):

        power = self.map_manager.check_power_up(position)

        if power is not None:
            power_message = {
                "type": MESSAGE_TYPES["UPDATE_POWER"],
                "player_id": player_id,
                "power": power,
                "grid": self.map_manager.get_grid()
            }

            self.network.broadcast(power_message, addr, send=True)

    def handle_bomb(self, data, addr):

        player_id = data["player_id"]

        if player_id is not None:
            bomb_data = {
                        "type": MESSAGE_TYPES["BOMB"],
                        "position": data["position"],
                        "player_id": data["player_id"],
                        "planted": data["planted"],
                    }

        self.network.broadcast(bomb_data, addr)

        with self.lock:
            self.bombs.append(bomb_data)
        
        self.handle_bomb_explosion(bomb_data, addr)
    
    def handle_bomb_explosion(self, bomb_data, addr):

        """
        Lida com a explosão de uma bomba após o tempo definido. A função calcula o tempo restante
        até a explosão e agenda a execução da explosão em um timer.

        Args:
            bomb_data (dict): Dados da bomba, incluindo posição e timer de explosão.
        """

        # Aguarda o tempo até a explosão
        explosion_time = bomb_data["planted"] + bomb_data.get("timer", 1) 
        time_to_wait = max(0, explosion_time - time.time())
    
        threading.Timer(time_to_wait, self.execute_bomb_explosion, args=(bomb_data, addr, )).start()

    def execute_bomb_explosion(self, bomb_data, addr):

        """
        Executa a explosão da bomba. Destrói as caixas ao redor da bomba e atualiza o grid do mapa
        para todos os jogadores.

        Args:
            bomb_data (dict): Dados da bomba que causou a explosão, incluindo a posição.
        """

        position = bomb_data["position"]

        # Sincronize acesso ao estado compartilhado (bombs, grid)
        with self.lock:
            self.map_manager.destroy_boxes_around(position)

        # Atualizar o grid para todos os clientes
        grid_data = {
            "type": MESSAGE_TYPES["GRID_UPDATE"],
            "grid": self.map_manager.get_grid()
        }

        self.network.broadcast(grid_data, addr, send=True)

    def handle_eliminated(self, data, addr):

        data = {
            "type": MESSAGE_TYPES["ELIMINATED"],
            "player_id": data["player_id"]
        }

        self.network.broadcast(data, addr, send=True)

    def handle_win(self, data, addr):

        """Gerencia as rodadas e define o vencedor final."""

        winner_id = data.get("winner_id")
        
        if winner_id is not None:

            self.player_wins[winner_id - 1] += 1

            print(self.player_wins)

            # Verifica se o jogador atingiu 3 vitórias
            if self.player_wins[winner_id - 1] == self.max_wins:
                self._reset_game_all(addr, winner_id)
            else:
                self._reset_round(winner_id, addr) 
           
    def _reset_round(self, winner_id, addr):


        """Reinicia o jogo para o próximo round, mantendo os jogadores conectados."""

        print(f"Rodada {self.current_round}: Jogador {winner_id} venceu!")
        self.current_round += 1

        # Reseta as posições dos jogadores
        for pid in self.player_data:
            self.player_data[pid]["position"] = PLAYER_POSITIONS[(pid - 1) % len(PLAYER_POSITIONS)]
            self.player_data[pid]["direction"] = "down"
            self.player_data[pid]["round_wins"] = self.player_wins[pid - 1]
        
        # Reseta o mapa para o estado inicial
        self.map_manager.reset_grid()

        # Envia atualização para todos os clientes
        round_reset_message = {
            "type": MESSAGE_TYPES["ROUND_RESET"],
            "round": self.current_round,
            "winner": winner_id,
            "players": self.player_data, 
            "grid": self.map_manager.get_grid()
        }

        self.network.broadcast(round_reset_message, addr, send=True)
        print(f"Round {self.current_round} reiniciado!")

    def _reset_game_all(self, addr, winner_id):

        game_over_message = {
            "type": MESSAGE_TYPES["GAME_OVER"],
            "round": self.current_round,
            "winner_id": winner_id,
            "players": self.player_data, 
        }

        self.network.broadcast(game_over_message, addr, send=True) 

        """Reinicia completamente o jogo após um jogador vencer 3 vezes."""

        self.player_data.clear()
        self.player_wins = [0] * self.network.max_clients
        self.current_round = 1
        self.map_manager = MapManager(random.choice(STAGES))
        self.game_in_progress = False
        print("Reset all")
        print("Jogo reiniciado!")
        self.network.disconnect_all()
