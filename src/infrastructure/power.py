from __future__ import annotations

from src.domain.models import BatteryStatus

import psutil


def verificar_bateria(logger=None) -> BatteryStatus:
    try:
        battery = psutil.sensors_battery()
        if battery is None:
            return BatteryStatus(True, "Sistema conectado a corriente (sin batería)")

        porcentaje = battery.percent
        conectado = battery.power_plugged

        if conectado:
            return BatteryStatus(True, f"Batería al {porcentaje}% y conectada a corriente")
        if porcentaje < 20:
            return BatteryStatus(False, f"Batería baja ({porcentaje}%). Conecta el cargador antes de continuar")
        if porcentaje < 50:
            return BatteryStatus(True, f"Batería al {porcentaje}%. Se recomienda conectar cargador para envíos largos")
        return BatteryStatus(True, f"Batería al {porcentaje}%")
    except Exception as exc:
        if logger:
            logger.warning(f"No se pudo verificar batería: {exc}")
        return BatteryStatus(True, "No se pudo verificar el estado de la batería")


def prevenir_suspension(logger=None) -> None:
    try:
        import ctypes

        ctypes.windll.kernel32.SetThreadExecutionState(0x80000000 | 0x00000001 | 0x00000002)
        if logger:
            logger.info("✓ Prevención de suspensión activada")
    except Exception as exc:
        if logger:
            logger.warning(f"No se pudo activar prevención de suspensión: {exc}")


def permitir_suspension(logger=None) -> None:
    try:
        import ctypes

        ctypes.windll.kernel32.SetThreadExecutionState(0x80000000)
        if logger:
            logger.info("✓ Sistema puede suspenderse nuevamente")
    except Exception as exc:
        if logger:
            logger.warning(f"No se pudo desactivar prevención de suspensión: {exc}")


def formatear_duracion(duracion_total_segundos: int) -> str:
    horas = duracion_total_segundos // 3600
    minutos = (duracion_total_segundos % 3600) // 60
    segundos = duracion_total_segundos % 60

    if horas > 0:
        return (
            f"{horas} hora{'s' if horas != 1 else ''} "
            f"{minutos} minuto{'s' if minutos != 1 else ''} "
            f"{segundos} segundo{'s' if segundos != 1 else ''}"
        )
    if minutos > 0:
        return f"{minutos} minuto{'s' if minutos != 1 else ''} {segundos} segundo{'s' if segundos != 1 else ''}"
    return f"{segundos} segundo{'s' if segundos != 1 else ''}"
