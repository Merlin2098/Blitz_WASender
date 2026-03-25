from __future__ import annotations

from dataclasses import dataclass, field
from typing import Optional


@dataclass(slots=True)
class MessageTemplate:
    id_mensaje: int
    mensaje: str


@dataclass(slots=True)
class ContactRecord:
    fila: int
    destinatario: str
    codigo_pais: str
    numero: str
    remitente: str
    id_mensaje: Optional[int]


@dataclass(slots=True)
class PreparedSend:
    fila_excel: int
    destinatario: str
    codigo_pais: str
    numero: str
    numero_completo: str
    mensaje: str
    remitente: str = ""
    id_mensaje: Optional[int] = None


@dataclass(slots=True)
class SendResult:
    fila_excel: int
    destinatario: str
    numero_completo: str
    estado: str
    mensaje_resultado: str
    timestamp: str


@dataclass(slots=True)
class CampaignExecutionTelemetry:
    mensajes_encontrados: int
    contactos_encontrados: int
    contactos_preparados: int


@dataclass(slots=True)
class CampaignExecutionSummary:
    total_contactos: int
    enviados: int
    fallidos: int
    tasa_exito: float
    ruta_reporte: str
    resultados: list[SendResult] = field(default_factory=list)


@dataclass(slots=True)
class BatteryStatus:
    puede_continuar: bool
    mensaje: str
