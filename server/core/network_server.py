import socket
import threading
import pickle

from config.constants import *

class NetworkServer:

    """Gerencia a comunicação de rede UDP do servidor."""
    
    def __init__(self, host=SERVER_IP, port=SERVER_PORT, max_clients=MAX_PLAYERS):

        self.host = host
        self.port = port
        self.server_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        self.server_socket.bind((self.host, self.port))
        self.clients = {}
        self.lock = threading.Lock()
        self.max_clients = max_clients

    def start_listening(self, message_handler):

        """Inicia a escuta de mensagens e chama o handler para processá-las."""

        print(f"Servidor UDP iniciado em {self.host}:{self.port}")

        while True:
            data, addr = self.server_socket.recvfrom(1024)
            try:
                data = pickle.loads(data) 
                message_handler(data, addr)
            except pickle.UnpicklingError:
                print("Erro ao desserializar a mensagem.")

    def send_message(self, message, addr):

        """Envia uma mensagem para um cliente específico."""

        try:
            serialized_message = pickle.dumps(message) 
            self.server_socket.sendto(serialized_message, addr)
        except pickle.PicklingError:
            print("Erro ao serializar a mensagem.")

    def broadcast(self, message, sender_addr, send=False):

        """Envia uma mensagem para todos os clientes. 
        Se send=True, também envia para o remetente."""

        with self.lock:
            for client_id, client_addr in self.clients.items():
                if send or client_addr != sender_addr:
                    self.send_message(message, client_addr)

    def register_client(self, addr):

        """Registra um novo cliente e retorna seu ID."""

        with self.lock:
            client_id = self.get_next_client_id()
            if client_id is not None:
                self.clients[client_id] = addr
                return client_id
            return None

    def unregister_client(self, addr):

        """Remove um cliente da lista de ativos."""

        with self.lock:
            for client_id, client_addr in list(self.clients.items()):
                if client_addr == addr:
                    del self.clients[client_id]
                    return client_id
        return None

    def get_next_client_id(self):

        """Retorna um ID disponível para um novo cliente."""

        for i in range(1, self.max_clients + 1):
            if i not in self.clients:
                return i
            
        return None
    
    def disconnect_all(self):

        """Desconecta todos os clientes sem enviar mensagens."""
        
        with self.lock:
            self.clients.clear()


