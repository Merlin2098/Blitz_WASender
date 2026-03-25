from __future__ import annotations

import os
import threading
import time
from pathlib import Path
from tkinter import filedialog, messagebox

from src.application.campaign_execution import CampaignExecutionService
from src.infrastructure.logging_support import log_seccion
from src.infrastructure.power import (
    formatear_duracion,
    permitir_suspension,
    prevenir_suspension,
    verificar_bateria,
)


class AppController:
    """
    Coordina las acciones de la UI principal sin contener widgets.
    """

    def __init__(
        self,
        window,
        logger,
        browser_service,
        paths,
        campaign_service_factory=CampaignExecutionService,
        thread_factory=threading.Thread,
    ):
        self.window = window
        self.logger = logger
        self.browser_service = browser_service
        self.paths = paths
        self.campaign_service_factory = campaign_service_factory
        self.thread_factory = thread_factory

    def seleccionar_excel(self) -> None:
        archivo = filedialog.askopenfilename(
            title="Seleccionar archivo Excel",
            filetypes=[("Excel files", "*.xlsx"), ("All files", "*.*")],
        )

        if archivo:
            self.window.ruta_excel = archivo
            self.window.entry_excel.delete(0, "end")
            self.window.entry_excel.insert(0, archivo)
            self.window.agregar_log(f"✓ Archivo seleccionado: {Path(archivo).name}")
            self.logger.info(f"Archivo Excel seleccionado: {archivo}")

    def configurar_perfil_navegador(self) -> None:
        try:
            navegador = self.window.combo_navegador.get()
            ruta_perfil = os.path.join(self.window.BASE_DIR, "perfiles", navegador.lower())
            perfil_existia = os.path.exists(ruta_perfil)
            ruta_perfil = self.browser_service.ensure_profile(navegador)

            if not perfil_existia:
                self.window.agregar_log(f"✓ Perfil creado: {ruta_perfil}")
                self.logger.info(f"Perfil creado para {navegador}: {ruta_perfil}")
                messagebox.showinfo(
                    "Perfil Creado",
                    f"Se ha creado el perfil para {navegador}\n\n"
                    f"Ruta: {ruta_perfil}\n\n"
                    f"Ahora puedes usar el botón 'Probar Navegador' para sincronizar WhatsApp.",
                )
            else:
                self.window.agregar_log(f"ℹ️ El perfil ya existe: {ruta_perfil}")
                messagebox.showinfo(
                    "Perfil Existente",
                    f"El perfil para {navegador} ya existe\n\n"
                    f"Ruta: {ruta_perfil}",
                )
        except Exception as exc:
            error_msg = f"Error al crear perfil: {exc}"
            self.window.agregar_log(f"✗ {error_msg}")
            self.logger.error(error_msg)
            messagebox.showerror("Error", error_msg)

    def probar_navegador(self) -> None:
        try:
            navegador = self.window.combo_navegador.get()
            self.browser_service.ensure_profile(navegador)

            self.window.agregar_log(f"🌐 Abriendo {navegador} para prueba...")
            self.logger.info(f"Abriendo {navegador} para configuración de WhatsApp")
            self.browser_service.launch_whatsapp_for_sync(navegador.lower())

            self.window.agregar_log(f"✓ {navegador} abierto en WhatsApp Web")
            self.window.agregar_log("ℹ️ Sincroniza tu cuenta y cierra el navegador cuando termines")

            messagebox.showinfo(
                "Navegador Abierto",
                f"{navegador} se ha abierto en WhatsApp Web\n\n"
                f"1. Escanea el código QR con tu teléfono\n"
                f"2. Espera a que cargue completamente\n"
                f"3. Cierra el navegador cuando termines\n\n"
                f"El perfil quedará guardado para futuros envíos.",
            )
        except Exception as exc:
            error_msg = f"Error al abrir navegador: {exc}"
            self.window.agregar_log(f"✗ {error_msg}")
            self.logger.error(error_msg)
            messagebox.showerror("Error", error_msg)

    def iniciar_proceso(self) -> None:
        if not self.window.ruta_excel:
            messagebox.showwarning("Advertencia", "Debes seleccionar un archivo Excel primero")
            return

        if not os.path.exists(self.window.ruta_excel):
            messagebox.showerror("Error", "El archivo seleccionado no existe")
            return

        self.window.navegador_seleccionado = self.window.combo_navegador.get()
        respuesta = messagebox.askyesno(
            "Confirmar Envío",
            f"¿Deseas iniciar el envío masivo?\n\n"
            f"Archivo: {Path(self.window.ruta_excel).name}\n"
            f"Navegador: {self.window.navegador_seleccionado}\n\n"
            f"Este proceso puede tardar varios minutos.",
        )

        if respuesta:
            self.window.agregar_log("=" * 50)
            self.window.agregar_log("🚀 Iniciando proceso de envío masivo...")
            self.window.agregar_log(f"📂 Archivo: {Path(self.window.ruta_excel).name}")
            self.window.agregar_log(f"🌐 Navegador: {self.window.navegador_seleccionado}")
            self.window.agregar_log("=" * 50)

            self.window.btn_iniciar.configure(state="disabled")
            self.window.label_info.configure(
                text="⏳ Procesando envío... Por favor espera",
                text_color=self.window.COLORES["amarillo"],
            )

            self.thread_factory(target=self.ejecutar_envio, daemon=True).start()

    def inicializar_driver(self):
        try:
            navegador = self.window.navegador_seleccionado.lower()
            ruta_perfil = self.browser_service.ensure_profile(navegador)

            self.window.agregar_log(f"Inicializando {self.window.navegador_seleccionado}...")
            self.window.agregar_log(f"Perfil: {ruta_perfil}")
            self.window.agregar_log("Selenium Manager gestionando driver automáticamente...")
            self.logger.info(f"Inicializando driver de {self.window.navegador_seleccionado}")
            self.logger.info(f"Perfil: {ruta_perfil}")
            self.logger.info("Selenium Manager auto-gestionando driver")

            driver = self.browser_service.initialize_driver(navegador)

            self.window.agregar_log(f"✓ {self.window.navegador_seleccionado} inicializado correctamente")
            self.logger.info(f"✓ Driver de {self.window.navegador_seleccionado} inicializado")
            return driver
        except Exception as exc:
            self.window.agregar_log(f"✗ Error al inicializar driver: {exc}")
            self.logger.error(f"Error al inicializar driver: {exc}")
            return None

    def ejecutar_envio(self) -> None:
        driver = None
        try:
            tiempo_inicio = time.time()
            battery_status = verificar_bateria(self.logger)
            self.window.agregar_log(f"🔋 {battery_status.mensaje}")
            self.logger.info(f"Estado de batería: {battery_status.mensaje}")

            if not battery_status.puede_continuar:
                self.window.agregar_log("⚠️ Proceso detenido: Batería insuficiente")
                messagebox.showwarning("Batería Baja", battery_status.mensaje)
                self.window.btn_iniciar.configure(state="normal")
                self.window.label_info.configure(
                    text="⚠️ Proceso detenido: Conecta el cargador e intenta nuevamente",
                    text_color=self.window.COLORES["amarillo"],
                )
                return

            prevenir_suspension(self.logger)
            self.window.agregar_log("✓ Prevención de suspensión activada")
            self.window.enviando = True
            self.window.cancelar_envio = False

            log_seccion(self.logger, f"INICIO DE ENVÍO MASIVO - {self.window.navegador_seleccionado}")
            self.logger.info(f"Navegador: {self.window.navegador_seleccionado}")
            self.logger.info(f"Archivo Excel: {self.window.ruta_excel}")
            self.logger.info("Driver: Selenium Manager (auto-gestionado)")

            self.window.agregar_log("\n🌐 Iniciando navegador...")
            log_seccion(self.logger, "INICIALIZACIÓN DE NAVEGADOR")
            driver = self.inicializar_driver()

            if not driver:
                self.window.agregar_log("✗ No se pudo inicializar el driver")
                messagebox.showerror("Error", "No se pudo inicializar el navegador")
                return

            self.window.agregar_log("\n📱 Abriendo WhatsApp Web...")
            driver.get("https://web.whatsapp.com")
            self.window.agregar_log("\n📤 Iniciando envío masivo...")
            log_seccion(self.logger, "ENVÍO MASIVO DE MENSAJES")

            campaign_service = self.campaign_service_factory(
                logger=self.logger,
                log_callback=self.window.agregar_log,
                logs_dir=self.window.LOGS_DIR,
            )
            summary, telemetry = campaign_service.execute(self.window.ruta_excel, driver)
            self.window.mensajes_dict = telemetry.mensajes_encontrados
            self.window.contactos_list = telemetry.contactos_encontrados

            log_seccion(self.logger, "RESUMEN FINAL")
            self.logger.info(f"Total procesados: {summary.total_contactos}")
            self.logger.info(f"Enviados exitosamente: {summary.enviados}")
            self.logger.info(f"Fallidos: {summary.fallidos}")
            self.logger.info(f"Tasa de éxito: {summary.tasa_exito:.1f}%")

            self.window.agregar_log(f"\n{'=' * 50}")
            self.window.agregar_log("RESUMEN FINAL:")
            self.window.agregar_log(f"  Total: {summary.total_contactos}")
            self.window.agregar_log(f"  Exitosos: {summary.enviados}")
            self.window.agregar_log(f"  Fallidos: {summary.fallidos}")
            self.window.agregar_log(f"  Tasa de éxito: {summary.tasa_exito:.1f}%")
            self.window.agregar_log(f"{'=' * 50}")

            permitir_suspension(self.logger)
            self.window.agregar_log("✓ Sistema puede suspenderse nuevamente")

            duracion_formateada = formatear_duracion(int(time.time() - tiempo_inicio))
            self.logger.info(f"⏱️ Tiempo total de ejecución: {duracion_formateada}")
            self.window.agregar_log(f"⏱️ Tiempo total de ejecución: {duracion_formateada}")

            if driver:
                driver.quit()
                driver = None
                self.window.agregar_log("✓ Navegador cerrado")

            self.window.notificar_finalizacion()
            messagebox.showinfo(
                "Proceso Completado",
                f"Envío masivo finalizado\n\n"
                f"Total: {summary.total_contactos}\n"
                f"Exitosos: {summary.enviados}\n"
                f"Fallidos: {summary.fallidos}\n\n"
                f"⏱️ Tiempo de ejecución: {duracion_formateada}\n\n"
                f"Revisa los reportes en la carpeta 'logs'",
            )
        except Exception as exc:
            self.window.agregar_log(f"✗ Error crítico: {exc}")
            self.logger.error(f"Error crítico: {exc}")
            messagebox.showerror("Error Crítico", f"Ocurrió un error crítico:\n{exc}")
        finally:
            if driver:
                try:
                    driver.quit()
                except Exception:
                    pass

            try:
                permitir_suspension(self.logger)
            except Exception:
                pass

            self.window.enviando = False
            self.window.btn_iniciar.configure(state="normal")
            self.window.label_info.configure(
                text="ℹ️ Proceso finalizado. Puedes iniciar un nuevo envío.",
                text_color=self.window.COLORES["gris_medio"],
            )
