"""
Pacote `player`

Responsável por gerenciar os jogadores no jogo.
Inclui:
- Representação de um jogador individual.
- Gerenciamento de múltiplos jogadores (adicionar, atualizar, remover).
"""

from .player import Player
from .player_manager import PlayerManager

__all__ = ["Player", "PlayerManager"]
