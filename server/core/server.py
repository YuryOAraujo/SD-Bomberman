import threading
import time
import random
from core.network_server import NetworkServer

from map.map_manager import MapManager

from config.constants import *

class Server:

    """
    A classe Server gerencia a lógica do servidor de jogo, lidando com as conexões de clientes,
    o estado do mapa e a lógica de bombas. A classe se comunica com os clientes e atualiza o estado
    do jogo em tempo real.
    """

    def __init__(self) -> None:

        """
        Inicializa o servidor, configurando os componentes de rede e mapa, além de preparar a
        estrutura para armazenar os dados dos jogadores e bombas.

        Variáveis:
            network_manager (NetworkServer): Gerencia as conexões de rede e comunicação com os clientes.
            map_manager (MapManager): Gerencia o estado do mapa do jogo, como destruição de caixas.
            player_data (list): Armazena os dados de posição e direção dos jogadores.
            bombs (list): Armazena os dados das bombas plantadas.
            bomb_lock (threading.Lock): Usado para garantir acesso exclusivo aos dados de bombas em um ambiente multithreaded.
        """

        self.network_manager = NetworkServer(HOST, PORT, MAX_PLAYERS)
        self.map_manager = MapManager(random.choice(STAGES))
        self.player_data = [{"position": (48, 48), "direction": "down"} for _ in range(MAX_PLAYERS)]
        self.bombs = []  
        self.bomb_lock = threading.Lock()

    def handle_bomb_explosion(self, bomb_data):

        """
        Lida com a explosão de uma bomba após o tempo definido. A função calcula o tempo restante
        até a explosão e agenda a execução da explosão em um timer.

        Args:
            bomb_data (dict): Dados da bomba, incluindo posição e timer de explosão.
        """

        # Aguarda o tempo até a explosão
        explosion_time = bomb_data["planted"] + bomb_data.get("timer", 1) 
        time_to_wait = max(0, explosion_time - time.time())
    
        threading.Timer(time_to_wait, self.execute_bomb_explosion, args=(bomb_data,)).start()

    def execute_bomb_explosion(self, bomb_data):

        """
        Executa a explosão da bomba. Destrói as caixas ao redor da bomba e atualiza o grid do mapa
        para todos os jogadores.

        Args:
            bomb_data (dict): Dados da bomba que causou a explosão, incluindo a posição.
        """

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

        """
        Lida com a comunicação contínua com um cliente. Recebe e processa os dados enviados pelo cliente,
        como atualizações de posição de jogadores e bombas.

        Args:
            client (socket.socket): O socket de conexão do cliente.
            player_id (int): O ID do jogador no servidor.
        """
        
        while True:
            data = self.network_manager.receive_data(client)
            if data is None:
                break
            
            if isinstance(data, dict):
                if data.get("type") == DATA_TYPE_BOMB:
                    bomb_data = {
                        "type": DATA_TYPE_BOMB,
                        "position": data["position"],
                        "player_id": data["player_id"],
                        "planted": data["planted"],
                    }
                    self.network_manager.broadcast(bomb_data)

                    # Adicionar a bomba com Lock
                    with self.bomb_lock:
                        self.bombs.append(bomb_data)

                    self.handle_bomb_explosion(bomb_data)
                elif data.get("type") == DATA_TYPE_PLAYER_UPDATE:
                    self.player_data[player_id] = {
                        "position": data["position"],
                        "direction": data["direction"]
                    }
                    data = {
                        "type": DATA_TYPE_PLAYER_DATA,
                        "players": self.player_data,
                        "grid": self.map_manager.get_grid()
                    }    
        
                    self.network_manager.broadcast(data)

                elif data.get("type") == "win":
                    self.map_manager.reset_grid()
                    data = {
                        "type": "win",
                        "grid": self.map_manager.get_grid()
                    }
                    print("Aqui")
                    self.network_manager.broadcast(data)
            else:
                print(f"Unexpected data format received: {data}")

    def on_client_connect(self, client, player_id):

        """
        Lida com a conexão de um novo cliente. Envia dados iniciais do jogo para o cliente e inicia
        a thread que gerenciará a comunicação com esse cliente.

        Args:
            client (socket.socket): O socket do cliente que se conectou.
            player_id (int): O ID do jogador que está se conectando.
        """

        self.network_manager.send_data(client, player_id)
        self.network_manager.send_data(client, (self.map_manager.get_grid(), self.map_manager.get_stage()))
        threading.Thread(target=self.handle_client, args=(client, player_id)).start()

    def run(self):

        """
        Inicia o servidor e começa a aceitar conexões de clientes. O servidor fica ouvindo
        por novas conexões de jogadores e gerencia suas interações.
        """

        print("Server running...")
        self.network_manager.accept_connections(self.on_client_connect)