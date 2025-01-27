import socket
import threading
import pickle
from grid_base import *
from random import randint

HOST = '127.0.0.1'
PORT = 5555
MAX_PLAYERS = 4

class Server:
    def __init__(self) -> None:
        self.server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.server.bind((HOST, PORT))
        self.server.listen(MAX_PLAYERS)
        self.clients = []
        self.grid = GRID_BASE["Stage 1"]
        self.player_data = [{"position": (48, 48), "direction": "down"} for _ in range(MAX_PLAYERS)]
        self.generate_boxes()   

    def broadcast(self, data) -> None:
        print(self.clients)
        for client in self.clients[:]:  
            try:
                if data.get("type") == "bomb":
                    print(f'Send: {data}')
                    print(client)
                client.send(pickle.dumps(data))
            except (BrokenPipeError, ConnectionResetError) as e:
                print(f"Error sending to client {client}: {e}")
                self.clients.remove(client)
            except pickle.PickleError as e:
                print(f"Serialization error: {e}")


    def handle_client(self, client, player_id) -> None:
        while True:
            try:
                data = pickle.loads(client.recv(4096))
                if isinstance(data, dict):
                    if data.get("type") == "bomb":
                        print(f'Receive: {data}')
                        bomb_data = {
                            "type": "bomb",
                            "position": data["position"],
                            "player_id": data["player_id"],
                            "planted": data["planted"],
                        }
                        self.broadcast(bomb_data)
                    elif data.get("type") == "player_update":
                        self.player_data[player_id] = {
                            "position": data["position"],
                            "direction": data["direction"]
                        }
                        data = {
                            "type": "player_data",
                            "players": self.player_data
                        }
                        self.broadcast(data)
                else:
                    print(f"Unexpected data format received: {data}")
            except (EOFError, ConnectionResetError) as e:
                print(f"Client {player_id} disconnected: {e}")
                self.clients.remove(client)
                break
            except pickle.UnpicklingError as e:
                print(f"Failed to decode data from client {player_id}: {e}")
            except KeyError as e:
                print(f"Invalid data received from client {player_id}: {e}")
                break



    def run(self) -> None:
        print("Server running...")
        while True:
            if len(self.clients) < MAX_PLAYERS:
                client, addr = self.server.accept()
                print(f"Player connected from {addr}")

                player_id = len(self.clients)
                self.clients.append(client)

                client.send(pickle.dumps(player_id))
                client.send(pickle.dumps(self.grid))

                thread = threading.Thread(target=self.handle_client, args=(client, player_id))
                thread.start()

    def generate_boxes(self) -> None:
        for row in range(1, len(self.grid) - 1):
            for col in range(1, len(self.grid[row]) - 1):
                if self.grid[row][col] != 0:
                    continue
                elif (row < 3 or row > len(self.grid) - 4) and (col < 3 or col > len(self.grid[row]) - 4):
                    continue
                if randint(0, 9) < 7:
                    self.grid[row][col] = 2

if __name__ == "__main__":
    Server().run()
