"""
Paquete de utilidades para WhatsApp Web Automation
Contiene módulos para logging, validación, manejo de Excel y envío de mensajes
"""

__version__ = "1.0.0"
__author__ = "Ricardo"

# Facilitar importaciones
from .logger import crear_logger
from .validators import (
    validar_archivo_existe,
    validar_extension,
    validar_numero_telefono,
    validar_estructura_excel
)
from .excel_handler import (
    leer_mensajes,
    leer_contactos,
    validar_hojas,
    generar_reporte
)
from .whatsapp_sender import WhatsAppSender

__all__ = [
    'crear_logger',
    'validar_archivo_existe',
    'validar_extension',
    'validar_numero_telefono',
    'validar_estructura_excel',
    'leer_mensajes',
    'leer_contactos',
    'validar_hojas',
    'generar_reporte',
    'WhatsAppSender'
]

"""
Utils Model - FrontEnd Components
"""
from .theme_manager import ThemeManager, get_theme_manager
from .ui_components import (
    ThemedButton,
    ThemedFrame,
    ThemedLabel,
    ThemedEntry,
    ThemedTextBox,
    ThemedProgressBar,
    FileSelector,
    ThemeToggleButton
)
from .ui_layout import UIBuilder

__all__ = [
    'ThemeManager',
    'get_theme_manager',
    'ThemedButton',
    'ThemedFrame',
    'ThemedLabel',
    'ThemedEntry',
    'ThemedTextBox',
    'ThemedProgressBar',
    'FileSelector',
    'ThemeToggleButton',
    'UIBuilder'
]