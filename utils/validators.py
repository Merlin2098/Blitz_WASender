"""
Wrapper de compatibilidad temporal para validaciones.
"""

from src.domain.validation import (
    validar_archivo_existe,
    validar_campos_mensaje,
    validar_estructura_excel,
    validar_extension,
    validar_id_mensaje_existe,
    validar_numero_telefono,
)

__all__ = [
    "validar_archivo_existe",
    "validar_campos_mensaje",
    "validar_estructura_excel",
    "validar_extension",
    "validar_id_mensaje_existe",
    "validar_numero_telefono",
]
