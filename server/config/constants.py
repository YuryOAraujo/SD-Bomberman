# Configurações do servidor

# Endereço IP do servidor local
HOST = '127.0.0.1'  

 # Porta utilizada pelo servidor
PORT = 5555 

# Número máximo de jogadores permitido na partida
MAX_PLAYERS = 4  

# Configurações do sprite

# Largura de cada sprite (em pixels)
SPRITE_WIDTH = 16  

 # Altura de cada sprite (em pixels)
SPRITE_HEIGHT = 16 

# Fator de escala para os sprites (ampliação)
SCALE = 3  

# Tipos de dados que são enviados e recebidos pelo servidor

# Usado para enviar/receber atualizações sobre o estado do jogador, como posição ou direção.
DATA_TYPE_PLAYER_UPDATE = "player_update"  

# Usado para enviar/receber informações relacionadas às bombas no jogo, como posição ou detonação.
DATA_TYPE_BOMB = "bomb"  

# Usado para atualizar o grid do jogo, como mudanças de obstáculos ou destruição de caixas.
DATA_TYPE_GRID_UPDATE = "grid_update"  

# Usado para enviar/receber dados gerais sobre o jogador, como nome, ID ou estado atual.
DATA_TYPE_PLAYER_DATA = "player_data"  

# Constante para definir os tipos de terreno no mapa
STAGES = ("Stage 1", "Stage 2")

 # Número da rodada inicial quando o jogo começa
INITIAL_ROUND = 1