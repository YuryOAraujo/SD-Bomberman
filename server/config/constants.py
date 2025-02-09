# Configurações do servidor

# Endereço IP do servidor local
SERVER_IP = '127.0.0.1'  

 # Porta utilizada pelo servidor
SERVER_PORT = 5555 

# Número máximo de jogadores permitido na partida
MAX_PLAYERS = 2  

# Configurações do sprite

# Largura de cada sprite (em pixels)
SPRITE_WIDTH = 16  

 # Altura de cada sprite (em pixels)
SPRITE_HEIGHT = 16 

# Fator de escala para os sprites (ampliação)
SCALE = 3  

# Constante para definir os tipos de terreno no mapa
STAGES = ("Stage 1", "Stage 2")

 # Número da rodada inicial quando o jogo começa
INITIAL_ROUND = 1

# Tipos de dados que são enviados e recebidos pelo servidor
MESSAGE_TYPES = {
    "CONNECT": "CONNECT",
    "GET_STATE": "GET_STATE",
    "START": "START",
    "GAME_IN_PROGRESS": "GAME_IN_PROGRESS",
    "FULL": "FULL",
    "DISCONNECTED": "DISCONNECTED",
    "BOMB": "BOMB",
    "UPDATE": "UPDATE",
    "GRID_UPDATE": "GRID_UPDATE",
    "WIN": "WIN",
    "UPDATE_POWER": "UPDATE_POWER",
    "ROUND_RESET": "ROUND_RESET",
    "ELIMINATED": "ELIMINATED",
    "GAME_OVER": "GAME_OVER"
}

PLAYER_POSITIONS = [
    (48, 48),
    (624, 48),
    (48, 624),
    (624, 624)
]