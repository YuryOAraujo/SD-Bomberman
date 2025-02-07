import socket
import pickle
from config.constants import *

class NetworkClient:

    """
    Classe responsável por gerenciar a conexão do cliente com o servidor do jogo.

    Essa classe fornece métodos para conectar ao servidor, enviar e receber dados,
    e gerenciar o ID do jogador atribuído pelo servidor.
    """
    
    def __init__(self, server_host, server_port):

        """
        Inicializa a instância do cliente de rede.

        Args:
            server_host (str): Endereço IP ou hostname do servidor.
            server_port (int): Porta do servidor.
        """

        self.client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.client.settimeout(5) 

        self.server_host = server_host
        self.server_port = server_port
        self.player_id = None

    def connect(self):

        """
        Conecta o cliente ao servidor.

        Returns:
            bool: Retorna True se a conexão for bem-sucedida, caso contrário, False.
        """

        try:
            self.client.connect((self.server_host, self.server_port))
            self.player_id = pickle.loads(self.client.recv(4096))
            print(f"Connected to server as Player {self.player_id}")
            return True
        except Exception as e:
            print(f"Failed to connect to server: {e}")
            return False

    def receive_data(self):

        """
        Recebe dados do servidor.

        Returns:
            object: Dados recebidos do servidor, desempacotados usando pickle.
            Retorna None em caso de erro.
        """

        try:
            raw_data = self.client.recv(4096)
            if not raw_data:
                print("Connection lost.")
                self.close()
                return None
            return pickle.loads(raw_data)
        except Exception as e:
            print(f"Failed to receive data: {e}")
            return None

    def send_data(self, data):

        """
        Envia dados para o servidor.

        Args:
            data (object): Dados a serem enviados, empacotados usando pickle.

        Raises:
            Exception: Fecha o cliente e encerra o programa em caso de erro.
        """

        try:
            self.client.send(pickle.dumps(data))
        except Exception as e:
            print(f"Failed to send data: {e}")
            self.client.close()
            exit()

    def close(self):

        """
        Fecha a conexão do cliente com o servidor.
        """
        
        self.client.close()