from __future__ import annotations

import logging
import os
import uuid
from dataclasses import dataclass
from datetime import datetime


@dataclass(slots=True)
class SessionLogContext:
    logger: logging.Logger
    log_path: str
    session_scope: str = "app_launch"


def create_session_logger(
    nombre: str,
    logs_dir: str,
    filename: str = "gui_app.log",
    overwrite: bool = True,
    nivel: int = logging.INFO,
) -> SessionLogContext:
    os.makedirs(logs_dir, exist_ok=True)
    log_path = os.path.join(logs_dir, filename)
    logger_name = f"{nombre}_{uuid.uuid4().hex}"
    logger = logging.getLogger(logger_name)
    logger.setLevel(nivel)
    logger.propagate = False

    file_mode = "w" if overwrite else "a"
    file_handler = logging.FileHandler(log_path, mode=file_mode, encoding="utf-8")
    file_handler.setLevel(nivel)

    console_handler = logging.StreamHandler()
    console_handler.setLevel(logging.WARNING)

    formato = logging.Formatter(
        "[%(asctime)s] [%(levelname)s] %(message)s",
        datefmt="%Y-%m-%d %H:%M:%S",
    )
    file_handler.setFormatter(formato)
    console_handler.setFormatter(formato)

    logger.addHandler(file_handler)
    logger.addHandler(console_handler)
    logger.info("=" * 70)
    logger.info("Inicio de sesión de aplicación")
    logger.info(f"Archivo de log: {log_path}")
    logger.info(f"Hora de inicio: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    logger.info("=" * 70)

    return SessionLogContext(logger=logger, log_path=log_path)


def close_session_logger(logger: logging.Logger, mensaje_final: str = "Sesión finalizada") -> None:
    logger.info("=" * 70)
    logger.info(mensaje_final)
    logger.info(f"Hora de finalización: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    logger.info("=" * 70)

    for handler in logger.handlers[:]:
        handler.close()
        logger.removeHandler(handler)
