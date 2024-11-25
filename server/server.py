import socket
import threading
import pickle

HOST = '127.0.0.1'
PORT = 5555
MAX_PLAYERS = 4

class Server:
    def __init__(self):
        self.server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.server.bind((HOST, PORT))
        self.server.listen(MAX_PLAYERS)
        self.clients = []
        self.player_data = [{"position": (400, 300), "direction": "down"} for _ in range(MAX_PLAYERS)]

    def broadcast(self):
        for client in self.clients:
            try:
                client.send(pickle.dumps(self.player_data))
            except:
                self.clients.remove(client)

    def handle_client(self, client, player_id):
        while True:
            try:
                data = pickle.loads(client.recv(1024))
                self.player_data[player_id] = data
                self.broadcast()
            except:
                self.clients.remove(client)
                break

    def run(self):
        print("Server running...")
        while True:
            if len(self.clients) < MAX_PLAYERS:
                client, addr = self.server.accept()
                print(f"Player connected from {addr}")

                player_id = len(self.clients)
                self.clients.append(client)
                client.send(pickle.dumps(player_id))

                thread = threading.Thread(target=self.handle_client, args=(client, player_id))
                thread.start()


if __name__ == "__main__":
    Server().run()
