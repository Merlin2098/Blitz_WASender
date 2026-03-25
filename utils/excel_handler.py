"""
Wrapper de compatibilidad temporal para manejo de Excel.
"""

from src.infrastructure.excel import (
    generar_reporte,
    generar_reporte_con_telemetria,
    leer_contactos,
    leer_mensajes,
    procesar_datos,
    validar_columnas,
    validar_hojas,
)

__all__ = [
    "generar_reporte",
    "generar_reporte_con_telemetria",
    "leer_contactos",
    "leer_mensajes",
    "procesar_datos",
    "validar_columnas",
    "validar_hojas",
]
