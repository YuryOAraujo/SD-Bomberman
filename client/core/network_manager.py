import socket
import pickle

from config.constants import *

class NetworkManager:

    def __init__(self, ip=SERVER_IP, port=SERVER_PORT, player_name=""):

        self.ip = ip
        self.port = port
        self.client_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        self.player_id = None
        self.player_name = player_name

    def connect(self):

        """Tenta conectar ao servidor e obter um ID."""

        message = {
            "type": MESSAGE_TYPES["CONNECT"],
            "name": self.player_name
        }
        
        self.send_message(message)
        
        # Espera pela resposta do servidor
        data, _ = self.client_socket.recvfrom(1024)

        try:
            # Desserializa a mensagem com pickle
            data = pickle.loads(data)  

            if isinstance(data, dict):

                message_type = data["type"]
                
                if message_type == MESSAGE_TYPES["CONNECT"]:
                    self.player_id = data["id"]
                return data    
            
        except pickle.UnpicklingError:
            print("Erro ao deserializar a mensagem.")
        return None

    def send_message(self, message):

        """Envia uma mensagem para o servidor utilizando pickle."""

        serialized_message = pickle.dumps(message)  # Serializa a mensagem com pickle
        self.client_socket.sendto(serialized_message, (self.ip, self.port))

    def receive_messages(self):

        """Escuta mensagens do servidor e chama um callback ao receber uma mensagem."""

        while True:
            data, _ = self.client_socket.recvfrom(1024)
            try:
                data = pickle.loads(data)  
                return data
            except pickle.UnpicklingError:
                print("Erro ao deserializar a mensagem.")

    def get_state(self):

        """Desconecta do servidor."""

        if self.player_id is not None:
            message = {"type": MESSAGE_TYPES["GET_STATE"]}
            self.send_message(message)
        
        data, _ = self.client_socket.recvfrom(1024)

        try:

            # Desserializa a mensagem com pickl
            data = pickle.loads(data)  

            # Verifica se a mensagem é um dicionário e contém o ID
            if isinstance(data, dict):
                return data["players"]
                
        except pickle.UnpicklingError:
            print("Erro ao deserializar a mensagem.")

        return None
        
    def disconnect(self):

        """Desconecta do servidor."""
        
        if self.player_id is not None:
            message = {"type": MESSAGE_TYPES["DISCONNECTED"]}
            self.send_message(message)
            self.player_id = None
