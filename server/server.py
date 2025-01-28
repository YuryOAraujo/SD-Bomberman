import threading
import time
from network_server import NetworkServer

from map_manager import MapManager

HOST = '127.0.0.1'
PORT = 5555
MAX_PLAYERS = 4

class Server:

    def __init__(self) -> None:
        self.network_manager = NetworkServer(HOST, PORT, MAX_PLAYERS)
        self.map_manager = MapManager("Stage 1")
        self.player_data = [{"position": (48, 48), "direction": "down"} for _ in range(MAX_PLAYERS)]
        self.bombs = []  
        self.bomb_lock = threading.Lock()

    def handle_bomb_explosion(self, bomb_data):

        """Lida com a explosão de uma bomba após o tempo definido."""

        # Aguarda o tempo até a explosão
        explosion_time = bomb_data["planted"] + bomb_data.get("timer", 1) 
        time_to_wait = max(0, explosion_time - time.time())
    
        threading.Timer(time_to_wait, self.execute_bomb_explosion, args=(bomb_data,)).start()

    def execute_bomb_explosion(self, bomb_data):

        position = bomb_data["position"]

        # Sincronize acesso ao estado compartilhado (bombs, grid)
        with self.bomb_lock:
            self.map_manager.destroy_boxes_around(position)

        # Atualizar o grid para todos os clientes
        grid_data = {
            "type": "grid_update",
            "grid": self.map_manager.get_grid()
        }

        self.network_manager.broadcast(grid_data)

    def handle_client(self, client, player_id):
        
        while True:
            data = self.network_manager.receive_data(client)
            if data is None:
                break

            if isinstance(data, dict):
                if data.get("type") == "bomb":
                    bomb_data = {
                        "type": "bomb",
                        "position": data["position"],
                        "player_id": data["player_id"],
                        "planted": data["planted"],
                    }
                    self.network_manager.broadcast(bomb_data)

                    # Adicionar a bomba com Lock
                    with self.bomb_lock:
                        self.bombs.append(bomb_data)

                    self.handle_bomb_explosion(bomb_data)
                elif data.get("type") == "player_update":
                    self.player_data[player_id] = {
                        "position": data["position"],
                        "direction": data["direction"]
                    }
                    data = {
                        "type": "player_data",
                        "players": self.player_data,
                        "grid": self.map_manager.get_grid()
                    }
                    self.network_manager.broadcast(data)
            else:
                print(f"Unexpected data format received: {data}")

    def on_client_connect(self, client, player_id):
        self.network_manager.send_data(client, player_id)
        self.network_manager.send_data(client, self.map_manager.get_grid())
        threading.Thread(target=self.handle_client, args=(client, player_id)).start()

    def run(self):
        print("Server running...")
        self.network_manager.accept_connections(self.on_client_connect)

if __name__ == "__main__":
    Server().run()