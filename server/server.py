# server.py
import socket
import threading
import pickle

HOST = '127.0.0.1'  # Localhost for now; change to your public IP for remote play
PORT = 5555
MAX_PLAYERS = 4

class Server:
    def __init__(self):
        self.server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.server.bind((HOST, PORT))
        self.server.listen(MAX_PLAYERS)
        self.clients = []
        self.player_positions = [(400, 300), (450, 300), (400, 350), (450, 350)]  # Starting positions

    def broadcast(self, data):
        for client in self.clients:
            try:
                client.send(pickle.dumps(data))
            except:
                self.clients.remove(client)

    def handle_client(self, client, player_id):
        while True:
            try:
                data = pickle.loads(client.recv(1024))
                self.player_positions[player_id] = data
                self.broadcast(self.player_positions)
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
                client.send(pickle.dumps(player_id))  # Send the player their ID

                thread = threading.Thread(target=self.handle_client, args=(client, player_id))
                thread.start()

if __name__ == "__main__":
    Server().run()
