"""
Wrapper de compatibilidad temporal para temas.
"""

from src.presentation.desktop.theme_manager import (
    ThemeManager,
    get_theme_manager,
    obtener_ruta_base,
    obtener_ruta_recurso,
)

__all__ = [
    "ThemeManager",
    "get_theme_manager",
    "obtener_ruta_base",
    "obtener_ruta_recurso",
]
