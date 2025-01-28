import socket
import pickle

class NetworkServer:
    def __init__(self, host, port, max_players):
        self.host = host
        self.port = port
        self.max_players = max_players
        self.server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.server.bind((self.host, self.port))
        self.server.listen(self.max_players)
        self.clients = []

    def accept_connections(self, on_connect_callback):
        print("Waiting for connections...")
        while True:
            if len(self.clients) < self.max_players:
                client, addr = self.server.accept()
                print(f"Player connected from {addr}")
                self.clients.append(client)
                on_connect_callback(client, len(self.clients) - 1)

    def send_data(self, client, data):
        try:
            client.send(pickle.dumps(data))
        except (BrokenPipeError, ConnectionResetError) as e:
            print(f"Error sending to client: {e}")
            self.clients.remove(client)
        except pickle.PickleError as e:
            print(f"Serialization error: {e}")

    def broadcast(self, data):
        for client in self.clients[:]:
            self.send_data(client, data)

    def receive_data(self, client):
        try:
            data = pickle.loads(client.recv(4096))
            return data
        except (EOFError, ConnectionResetError) as e:
            print(f"Client disconnected: {e}")
            self.clients.remove(client)
            return None
        except pickle.UnpicklingError as e:
            print(f"Failed to decode data from client: {e}")
            return None

    def close(self):
        for client in self.clients:
            client.close()
        self.server.close()