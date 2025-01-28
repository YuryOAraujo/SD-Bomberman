"""
Pacote `ui`

Gerencia a interface do usuário no jogo.

Inclui:

- HUD (heads-up display) e elementos gráficos.
- Menus (principal, configurações, etc.).
"""

from .game_ui import GameUI
from .menu import Menu

__all__ = ["GameUI", "Menu"]
