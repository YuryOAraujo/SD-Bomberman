import socket
import pickle

class NetworkServer:

    """
    A classe NetworkServer gerencia o servidor de rede para um jogo multiplayer,
    fornecendo métodos para aceitar conexões de jogadores, enviar e receber dados.
    """

    def __init__(self, host, port, max_players):

        """
        Inicializa o servidor de rede com o endereço do host, porta e o número máximo de jogadores permitidos.

        Args:
            host (str): O endereço IP do servidor (geralmente '127.0.0.1' para localhost).
            port (int): A porta em que o servidor irá escutar por conexões.
            max_players (int): O número máximo de jogadores que podem se conectar ao servidor.
        """

        self.host = host
        self.port = port
        self.max_players = max_players
        self.server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.server.bind((self.host, self.port))
        self.server.listen(self.max_players)
        self.clients = []

    def accept_connections(self, on_connect_callback):

        """
        Aceita as conexões dos clientes, adicionando-os à lista de clientes conectados.
        Chama o callback fornecido sempre que um jogador se conecta.

        Args:
            on_connect_callback (function): Função callback que é chamada quando um cliente se conecta.
                A função recebe dois parâmetros: o cliente conectado e o índice do cliente na lista.
        """

        print("Waiting for connections...")
        while True:
            if len(self.clients) < self.max_players:
                client, addr = self.server.accept()
                print(f"Player connected from {addr}")
                self.clients.append(client)
                on_connect_callback(client, len(self.clients) - 1)

    def send_data(self, client, data):

        """
        Envia dados para um cliente específico após serializá-los com pickle.

        Args:
            client (socket.socket): O socket do cliente para o qual os dados serão enviados.
            data (any): Os dados a serem enviados para o cliente.

        Exceções:
            BrokenPipeError, ConnectionResetError: Ocorrem se a conexão com o cliente for interrompida.
            pickle.PickleError: Ocorre se houver um erro ao serializar os dados.
        """

        try:
            client.send(pickle.dumps(data))
        except (BrokenPipeError, ConnectionResetError) as e:
            print(f"Error sending to client: {e}")
            self.clients.remove(client)
        except pickle.PickleError as e:
            print(f"Serialization error: {e}")

    def broadcast(self, data):

        """
        Envia os dados para todos os clientes conectados.

        Args:
            data (any): Os dados a serem enviados para todos os clientes.
        """

        for client in self.clients[:]:
            self.send_data(client, data)

    def receive_data(self, client):
        
        """
        Recebe dados de um cliente, tentando deserializar os dados recebidos.

        Args:
            client (socket.socket): O socket do cliente de onde os dados serão recebidos.

        Retorna:
            any: Os dados recebidos e desserializados do cliente, ou None em caso de erro.
        
        Exceções:
            EOFError, ConnectionResetError: Ocorrem quando a conexão do cliente é fechada ou reiniciada.
            pickle.UnpicklingError: Ocorre se os dados recebidos não puderem ser deserializados corretamente.
        """

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

        """
        Fecha as conexões com todos os clientes e o servidor.
        """
        
        for client in self.clients:
            client.close()
        self.server.close()