"""
Módulo para gestión de logs
Crea logs únicos por cada ejecución con timestamp
Soporte para rutas dinámicas (desarrollo vs PyInstaller)
VERSIÓN SPRINT 1: Naming dinámico DD.MM.YYYY_HH.MM.SS + retorno tupla
"""

import logging
import os
import sys
import time
from datetime import datetime


def obtener_ruta_base():
    """
    Retorna la ruta base según el entorno:
    - Si es .exe (PyInstaller): carpeta donde está el ejecutable
    - Si es Python: raíz del proyecto
    
    Returns:
        str: Ruta base absoluta
    """
    if getattr(sys, 'frozen', False):
        # Ejecutándose desde PyInstaller (.exe)
        return os.path.dirname(sys.executable)
    else:
        # Ejecutándose desde Python
        # Subir un nivel desde utils/ hasta la raíz del proyecto
        return os.path.dirname(os.path.dirname(os.path.abspath(__file__)))


def crear_logger_con_naming(nombre_base, carpeta="logs", nivel=logging.INFO):
    """
    Crea un logger con archivo único basado en timestamp formato DD.MM.YYYY_HH.MM.SS.
    La carpeta se crea en la ruta base del proyecto o junto al .exe.
    
    CAMBIOS SPRINT 1:
    - Formato timestamp: DD.MM.YYYY_HH.MM.SS (antes: YYYYMMDD_HHMMSS)
    - Retorna tupla: (logger, ruta_log) (antes: solo logger)
    
    Args:
        nombre_base (str): Nombre base del log (ej: 'envio_masivo')
        carpeta (str): Nombre de la carpeta donde guardar los logs (relativo a ruta base)
        nivel: Nivel de logging (INFO, DEBUG, ERROR, etc.)
    
    Returns:
        tuple: (logging.Logger, str) - (Logger configurado, ruta completa del archivo log)
    """
    # Obtener ruta base y construir ruta completa de logs
    ruta_base = obtener_ruta_base()
    
    # Si carpeta es una ruta absoluta, usarla directamente
    # Si no, construirla relativa a ruta_base
    if os.path.isabs(carpeta):
        ruta_logs = carpeta
    else:
        ruta_logs = os.path.join(ruta_base, carpeta)
    
    # Crear carpeta de logs si no existe
    if not os.path.exists(ruta_logs):
        os.makedirs(ruta_logs)
    
    # Generar nombre de archivo con timestamp único en formato DD.MM.YYYY_HH.MM.SS
    timestamp = datetime.now().strftime('%d.%m.%Y_%H.%M.%S')
    nombre_archivo = f"{nombre_base}_{timestamp}.log"
    ruta_log = os.path.join(ruta_logs, nombre_archivo)
    
    # Crear logger con nombre único
    logger = logging.getLogger(nombre_base + "_" + timestamp)
    logger.setLevel(nivel)
    
    # Evitar duplicar handlers si el logger ya existe
    if logger.handlers:
        return logger, ruta_log
    
    # Handler para archivo
    file_handler = logging.FileHandler(ruta_log, encoding='utf-8')
    file_handler.setLevel(nivel)
    
    # Handler para consola
    console_handler = logging.StreamHandler()
    console_handler.setLevel(logging.WARNING)  # Solo warnings y errores en consola
    
    # Formato del log
    formato = logging.Formatter(
        '[%(asctime)s] [%(levelname)s] %(message)s',
        datefmt='%Y-%m-%d %H:%M:%S'
    )
    file_handler.setFormatter(formato)
    console_handler.setFormatter(formato)
    
    # Agregar handlers
    logger.addHandler(file_handler)
    logger.addHandler(console_handler)
    
    # Log inicial
    logger.info("=" * 70)
    logger.info(f"Inicio de log: {nombre_archivo}")
    logger.info(f"Ruta: {ruta_log}")
    logger.info("=" * 70)
    
    return logger, ruta_log


def crear_logger(nombre_base, carpeta="logs", nivel=logging.INFO):
    """
    Mantiene compatibilidad con código antiguo.
    Llama a crear_logger_con_naming() pero solo retorna el logger.
    
    DEPRECADO: Usar crear_logger_con_naming() para obtener también la ruta.
    
    Args:
        nombre_base (str): Nombre base del log
        carpeta (str): Carpeta de logs
        nivel: Nivel de logging
    
    Returns:
        logging.Logger: Logger configurado
    """
    logger, _ = crear_logger_con_naming(nombre_base, carpeta, nivel)
    return logger


def log_separador(logger, caracter="=", longitud=70):
    """
    Agrega una línea separadora al log.
    
    Args:
        logger: Logger instance
        caracter (str): Carácter para la línea
        longitud (int): Longitud de la línea
    """
    logger.info(caracter * longitud)


def log_seccion(logger, titulo):
    """
    Agrega un título de sección destacado en el log.
    
    Args:
        logger: Logger instance
        titulo (str): Título de la sección
    """
    log_separador(logger)
    logger.info(f"  {titulo.upper()}")
    log_separador(logger)


def log_error_detallado(logger, mensaje, excepcion=None):
    """
    Registra un error con detalles de la excepción si existe.
    
    Args:
        logger: Logger instance
        mensaje (str): Mensaje de error
        excepcion (Exception): Excepción capturada (opcional)
    """
    logger.error(mensaje)
    if excepcion:
        logger.error(f"Tipo: {type(excepcion).__name__}")
        logger.error(f"Detalle: {str(excepcion)}")


def log_progreso(logger, actual, total, mensaje=""):
    """
    Registra el progreso de una operación.
    
    Args:
        logger: Logger instance
        actual (int): Número actual
        total (int): Total de elementos
        mensaje (str): Mensaje adicional
    """
    porcentaje = (actual / total * 100) if total > 0 else 0
    info = f"Progreso: {actual}/{total} ({porcentaje:.1f}%)"
    if mensaje:
        info += f" - {mensaje}"
    logger.info(info)


def cerrar_logger(logger, mensaje_final="Proceso finalizado"):
    """
    Cierra el logger con un mensaje final.
    
    Args:
        logger: Logger instance
        mensaje_final (str): Mensaje de cierre
    """
    log_separador(logger)
    logger.info(mensaje_final)
    logger.info(f"Hora de finalización: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    log_separador(logger)
    
    # Cerrar handlers
    for handler in logger.handlers[:]:
        handler.close()
        logger.removeHandler(handler)