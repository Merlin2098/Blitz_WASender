from __future__ import annotations

from dataclasses import asdict
import time
from datetime import datetime
from pathlib import Path

from src.domain.models import CampaignExecutionSummary, CampaignExecutionTelemetry, SendResult
from src.infrastructure.excel import generar_reporte, leer_contactos, leer_mensajes, procesar_datos
from src.infrastructure.whatsapp_web import WhatsAppWebClient


class CampaignExecutionService:
    """
    Orquesta la ejecución completa de una campaña de envío.
    """

    def __init__(self, logger, log_callback, logs_dir: str):
        self.logger = logger
        self.log_callback = log_callback
        self.logs_dir = logs_dir

    def execute(self, ruta_excel: str, driver) -> tuple[CampaignExecutionSummary, CampaignExecutionTelemetry]:
        self.log_callback("\n📖 Leyendo datos del Excel...")
        mensajes_dict = leer_mensajes(ruta_excel, self.logger)
        contactos_list = leer_contactos(ruta_excel, self.logger)

        self.logger.info(f"Mensajes encontrados: {len(mensajes_dict)}")
        self.logger.info(f"Contactos encontrados: {len(contactos_list)}")
        self.log_callback(f"✓ {len(mensajes_dict)} mensajes encontrados")
        self.log_callback(f"✓ {len(contactos_list)} contactos encontrados")

        self.log_callback("\n⚙️ Procesando datos...")
        datos_procesados, errores = procesar_datos(contactos_list, mensajes_dict, self.logger)
        if errores:
            self.log_callback(f"⚠️ {len(errores)} errores de procesamiento")

        total_contactos = len(datos_procesados)
        self.log_callback(f"✓ {total_contactos} envíos preparados")
        self.logger.info(f"Total de envíos a procesar: {total_contactos}")

        if total_contactos == 0:
            raise ValueError("No se encontraron datos válidos para enviar")

        self.log_callback("\n📤 Iniciando envío masivo...")
        sender = WhatsAppWebClient(driver, self.logger)

        if not sender.wait_until_ready(timeout=60):
            raise RuntimeError("WhatsApp Web no cargó. ¿Escaneaste el código QR?")

        self.log_callback("✓ WhatsApp Web cargado correctamente")

        enviados = 0
        fallidos = 0
        resultados: list[SendResult] = []

        for idx, datos in enumerate(datos_procesados, 1):
            try:
                self.log_callback(f"\n[{idx}/{total_contactos}] Enviando a {datos['destinatario']}...")
                exito, mensaje_resultado = sender.send_prefilled_message(
                    datos["codigo_pais"],
                    datos["numero"],
                    datos["mensaje"],
                )

                if exito:
                    enviados += 1
                    estado = "EXITOSO"
                    self.log_callback("✓ Enviado exitosamente")
                else:
                    fallidos += 1
                    estado = "FALLIDO"
                    self.log_callback(f"✗ Falló: {mensaje_resultado}")

                resultados.append(
                    SendResult(
                        fila_excel=datos["fila_excel"],
                        destinatario=datos["destinatario"],
                        numero_completo=datos["numero_completo"],
                        estado=estado,
                        mensaje_resultado=mensaje_resultado,
                        timestamp=datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                    )
                )

                if idx < total_contactos:
                    sender.apply_random_delay()

            except Exception as exc:
                fallidos += 1
                self.logger.error(f"Error inesperado con {datos['destinatario']}: {exc}")
                self.log_callback(f"✗ Error inesperado: {exc}")
                resultados.append(
                    SendResult(
                        fila_excel=datos.get("fila_excel", "N/A"),
                        destinatario=datos.get("destinatario", "Desconocido"),
                        numero_completo=datos.get("numero_completo", "N/A"),
                        estado="FALLIDO",
                        mensaje_resultado=f"Excepción: {exc}",
                        timestamp=datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                    )
                )

        self.log_callback("\n📊 Generando reporte...")
        ruta_reporte = generar_reporte(
            [asdict(resultado) for resultado in resultados],
            carpeta=self.logs_dir,
            nombre_base="envios_whatsapp",
        )
        self.log_callback(f"✓ Reporte generado: {Path(ruta_reporte).name}")

        tasa_exito = (enviados / total_contactos * 100) if total_contactos > 0 else 0
        summary = CampaignExecutionSummary(
            total_contactos=total_contactos,
            enviados=enviados,
            fallidos=fallidos,
            tasa_exito=tasa_exito,
            ruta_reporte=ruta_reporte,
            resultados=resultados,
        )
        telemetry = CampaignExecutionTelemetry(
            mensajes_encontrados=len(mensajes_dict),
            contactos_encontrados=len(contactos_list),
            contactos_preparados=total_contactos,
        )
        return summary, telemetry
