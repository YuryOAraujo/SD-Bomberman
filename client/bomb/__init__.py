"""
Pacote `bomb`

Este pacote gerencia todas as funcionalidades relacionadas às bombas no jogo.
Inclui:
- Lógica de bombas individuais.
- Gerenciamento global de bombas (criação, atualização e remoção).
"""

from .bomb import Bomb
from .bomb_manager import BombManager

__all__ = ["Bomb", "BombManager"]
