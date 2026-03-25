"""
Namespace de compatibilidad temporal para utilidades heredadas.
"""

from .excel_handler import generar_reporte, leer_contactos, leer_mensajes, procesar_datos, validar_hojas
from .logger import cerrar_logger, crear_logger, log_seccion, log_separador
from .theme_manager import ThemeManager, get_theme_manager
from .ui_components import (
    FileSelector,
    ThemeToggleButton,
    ThemedButton,
    ThemedEntry,
    ThemedFrame,
    ThemedLabel,
    ThemedProgressBar,
    ThemedTextBox,
)
from .ui_layout import UIBuilder
from .validators import (
    validar_archivo_existe,
    validar_campos_mensaje,
    validar_estructura_excel,
    validar_extension,
    validar_id_mensaje_existe,
    validar_numero_telefono,
)
from .whatsapp_sender import WhatsAppSender

__version__ = "2.0.0"
__author__ = "Ricardo"

__all__ = [
    "FileSelector",
    "ThemeManager",
    "ThemeToggleButton",
    "ThemedButton",
    "ThemedEntry",
    "ThemedFrame",
    "ThemedLabel",
    "ThemedProgressBar",
    "ThemedTextBox",
    "UIBuilder",
    "WhatsAppSender",
    "cerrar_logger",
    "crear_logger",
    "generar_reporte",
    "get_theme_manager",
    "leer_contactos",
    "leer_mensajes",
    "log_seccion",
    "log_separador",
    "procesar_datos",
    "validar_archivo_existe",
    "validar_campos_mensaje",
    "validar_estructura_excel",
    "validar_extension",
    "validar_hojas",
    "validar_id_mensaje_existe",
    "validar_numero_telefono",
]
