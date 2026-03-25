import unittest
from unittest.mock import MagicMock, patch

from src.application.campaign_execution import CampaignExecutionService


class CampaignExecutionServiceTests(unittest.TestCase):
    @patch("src.application.campaign_execution.generar_reporte", return_value="logs/envios_whatsapp.xlsx")
    @patch("src.application.campaign_execution.procesar_datos")
    @patch("src.application.campaign_execution.leer_contactos")
    @patch("src.application.campaign_execution.leer_mensajes")
    @patch("src.application.campaign_execution.WhatsAppWebClient")
    def test_execute_serializes_send_results_with_slots_dataclass(
        self,
        whatsapp_client_cls,
        leer_mensajes,
        leer_contactos,
        procesar_datos,
        generar_reporte,
    ):
        leer_mensajes.return_value = {1: {"mensaje": "hola"}}
        leer_contactos.return_value = [{"fila_excel": 2, "destinatario": "Ricardo"}]
        procesar_datos.return_value = (
            [
                {
                    "fila_excel": 2,
                    "destinatario": "Ricardo",
                    "codigo_pais": "51",
                    "numero": "999999999",
                    "numero_completo": "51999999999",
                    "mensaje": "hola",
                }
            ],
            [],
        )

        whatsapp_client = MagicMock()
        whatsapp_client.wait_until_ready.return_value = True
        whatsapp_client.send_prefilled_message.return_value = (True, "OK")
        whatsapp_client_cls.return_value = whatsapp_client

        service = CampaignExecutionService(
            logger=MagicMock(),
            log_callback=lambda _msg: None,
            logs_dir="logs",
        )

        summary, telemetry = service.execute("dummy.xlsx", driver=MagicMock())

        self.assertEqual(summary.enviados, 1)
        self.assertEqual(telemetry.contactos_preparados, 1)
        report_rows = generar_reporte.call_args.args[0]
        self.assertEqual(report_rows[0]["destinatario"], "Ricardo")
        self.assertEqual(report_rows[0]["estado"], "EXITOSO")


if __name__ == "__main__":
    unittest.main()
