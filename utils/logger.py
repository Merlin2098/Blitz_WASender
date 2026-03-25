"""
Wrapper de compatibilidad temporal para logging.
"""

from src.infrastructure.logging_support import (
    cerrar_logger,
    crear_logger,
    crear_logger_con_naming,
    log_error_detallado,
    log_progreso,
    log_seccion,
    log_separador,
    obtener_ruta_base,
)

__all__ = [
    "cerrar_logger",
    "crear_logger",
    "crear_logger_con_naming",
    "log_error_detallado",
    "log_progreso",
    "log_seccion",
    "log_separador",
    "obtener_ruta_base",
]
