"""
Pacote `core`

Contém os componentes principais do jogo:

- Lógica geral do jogo.
- Gerenciamento do loop principal.
- Comunicação em rede para multiplayer.

"""

from .game import Game
from .network_client import NetworkClient

__all__ = ["Game", "NetworkClient"]