# Configurações principais do jogo

# Largura da janela do jogo
WIDTH = 720  

# Altura da janela do jogo
HEIGHT = 680  

UI_WIDTH = 350  # Largura da interface
UI_HEIGHT = HEIGHT  # A interface tem a mesma altura do mapa

TOTAL_WIDTH = UI_WIDTH + WIDTH
TOTAL_HEIGHT = HEIGHT

 # Área jogável disponível (provavelmente igual à altura da janela)
PLAYABLE_AREA_HEIGHT = 624 

# Área jogável disponível (provavelmente igual à largura da janela)
PLAYABLE_AREA_WIDTH = 720 

 # Taxa de quadros por segundo (frames per second), controla a fluidez do jogo
FPS = 60 

# Título da janela do jogo
TITLE = "SD-Bomberman"  

# Cor branca em RGB
WHITE = (255, 255, 255)  

# Cor rosa em RGB
PINK = (255, 0, 255)

 # Largura de cada sprite (imagem de personagem ou objeto)
SPRITE_WIDTH = 16 

# Altura de cada sprite
SPRITE_HEIGHT = 16  

# Fator de escala para aumentar o tamanho dos sprites na tela
SCALE = 3  

# Número de quadros na animação do jogador
PLAYER_ANIMATION_LENGTH = 10  

# Margem em pixels para a borda da tela ou do grid
PIXEL_EDGE = 15  

# Caminho para os sprites (imagens usadas no jogo)
PATH_SPRITES = "client/assets/sprites/bomb_party_v3.png"

PATH_ICON_HEART = "client/assets/icons/heart.png"

PATH_BACKGROUND = "client/assets/background/Fundo.png"

PATH_TROPHY = "client/assets/icons/trofeu.png"

PATH_ICON_INFO = "client/assets/icons/information.png"

# Configurações de rede

 # Endereço IP do servidor
SERVER_IP = '127.0.0.1' 

# Porta de comunicação do servidor com o cliente
SERVER_PORT = 5555  

# Configurações de rodadas

 # Número da rodada inicial quando o jogo começa
INITIAL_ROUND = 0 

 # Número máximo de vitórias necessárias para ganhar o jogo
MAX_WINS = 3 

# Tipos de dados enviados ao servidor

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
    "UPDATE_POWER": "UPDATE_POWER",
    "WIN": "WIN",
    "ROUND_RESET": "ROUND_RESET",
    "ELIMINATED": "ELIMINATED",
    "GAME_OVER": "GAME_OVER",
    "MAP_CHOICE": "MAP_CHOICE"
}

# Dados padrão da bomba

# Estado inicial da bomba, indicando que ela ainda não foi plantada
BOMB_DEFAULT_PLANTED = False  
