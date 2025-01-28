"""
Pacote `core`

Contém o núcleo do servidor:
- `server`: Controla o loop principal e a lógica geral.
- `network_server`: Gerencia conexões de rede com os clientes.
"""

from .server import Server
from .network_server import NetworkServer

__all__ = ["Server", "NetworkServer"]