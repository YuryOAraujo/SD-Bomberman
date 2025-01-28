import socket
import pickle
from config.constants import *

class NetworkClient:
    
    def __init__(self, server_host, server_port):
        self.client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.server_host = server_host
        self.server_port = server_port
        self.player_id = None

    def connect(self):
        try:
            self.client.connect((self.server_host, self.server_port))
            self.player_id = pickle.loads(self.client.recv(4096))
            print(f"Connected to server as Player {self.player_id}")
            return True
        except Exception as e:
            print(f"Failed to connect to server: {e}")
            return False

    def receive_data(self):
        try:
            data = pickle.loads(self.client.recv(4096))
            return data
        except Exception as e:
            print(f"Failed to receive data: {e}")
            return None

    def send_data(self, data):
        try:
            self.client.send(pickle.dumps(data))
        except Exception as e:
            print(f"Failed to send data: {e}")
            self.client.close()
            exit()

    def close(self):
        self.client.close()