from __future__ import annotations

import customtkinter as ctk
import threading
import time
from datetime import datetime

from src.application.browser_session import BrowserSessionService
from src.application.campaign_execution import CampaignExecutionService
from src.presentation.desktop.app_controller import AppController
from src.presentation.desktop.theme_manager import get_theme_manager
from src.presentation.desktop.theme_service import DesktopThemeService
from src.presentation.desktop.ui_sections import DesktopUISections


class MainWindow(ctk.CTk):
    """
    Ventana principal de la aplicación desktop.
    """

    def __init__(
        self,
        logger,
        paths,
        browser_service: BrowserSessionService | None = None,
        campaign_service_factory=CampaignExecutionService,
        theme_manager=None,
    ):
        super().__init__()

        self.logger = logger
        self.paths = paths
        self.browser_service = browser_service or BrowserSessionService()
        self.theme_manager = theme_manager or get_theme_manager(default_theme="dark")
        self.campaign_service_factory = campaign_service_factory
        self.ui_sections = DesktopUISections(self)
        self.controller = AppController(
            window=self,
            logger=self.logger,
            browser_service=self.browser_service,
            paths=self.paths,
            campaign_service_factory=self.campaign_service_factory,
        )

        self.ruta_excel = None
        self.navegador_seleccionado = "Edge"
        self.mensajes_dict = None
        self.contactos_list = None
        self.datos_procesados = None
        self.driver = None
        self.enviando = False
        self.cancelar_envio = False
        self.theme_buttons = {}
        self.BASE_DIR = self.paths.get_base_dir()
        self.LOGS_DIR = self.paths.get_logs_dir()

        self._configure_window()
        self.configurar_colores()
        self.iniciar_lazy_loading()

    def _configure_window(self) -> None:
        self.title("Blitz WaSender: Herramienta de Envío Masivo de Mensajes (v2.3)")
        self.geometry("900x750")
        self.minsize(800, 650)
        self.state("zoomed")
        self.after(100, lambda: self.wm_attributes("-alpha", 0.99))
        self.after(200, lambda: self.wm_attributes("-alpha", 1.0))
        self._configure_caption_color()
        self._configure_icon()
        self.lift()
        self.focus_force()
        self.attributes("-topmost", True)
        self.after(300, lambda: self.attributes("-topmost", False))

    def _configure_caption_color(self) -> None:
        try:
            import ctypes

            ctypes.windll.dwmapi.DwmSetWindowAttribute(
                ctypes.windll.user32.GetParent(self.winfo_id()),
                35,
                ctypes.byref(ctypes.c_int(0xE0E0E0)),
                ctypes.sizeof(ctypes.c_int),
            )
        except Exception:
            pass

    def _configure_icon(self) -> None:
        try:
            icon_path = self.paths.get_resource_path("app_icon.ico")
            if icon_path:
                self.iconbitmap(icon_path)
        except Exception as exc:
            self.logger.warning(f"No se pudo cargar el ícono: {exc}")

    def configurar_colores(self) -> None:
        DesktopThemeService.configure_window(self)

    def iniciar_lazy_loading(self) -> None:
        self.loading_frame = ctk.CTkFrame(self, fg_color=self.COLORES["bg_principal"])
        self.loading_frame.pack(fill="both", expand=True)

        self.loading_label = ctk.CTkLabel(
            self.loading_frame,
            text="Cargando aplicación...",
            font=("Segoe UI", 20, "bold"),
            text_color=self.COLORES["turquesa"],
        )
        self.loading_label.pack(pady=(250, 20))

        self.loading_progress = ctk.CTkProgressBar(
            self.loading_frame,
            width=400,
            height=8,
            corner_radius=4,
            progress_color=self.COLORES["turquesa"],
        )
        self.loading_progress.pack(pady=10)
        self.loading_progress.set(0)

        self.loading_status = ctk.CTkLabel(
            self.loading_frame,
            text="Iniciando...",
            font=("Segoe UI", 12),
            text_color=self.COLORES["gris_medio"],
        )
        self.loading_status.pack(pady=10)

        threading.Thread(target=self.ejecutar_lazy_loading, daemon=True).start()

    def ejecutar_lazy_loading(self) -> None:
        try:
            self.loading_status.configure(text="Cargando estructura básica...")
            self.loading_progress.set(0.33)
            time.sleep(0.3)

            self.loading_status.configure(text="Cargando componentes...")
            self.loading_progress.set(0.66)
            time.sleep(0.3)

            self.loading_status.configure(text="Finalizando...")
            self.loading_progress.set(1.0)
            time.sleep(0.3)
            self.after(0, self.finalizar_lazy_loading)
        except Exception as exc:
            self.logger.error(f"Error en lazy loading: {exc}")
            self.after(0, self.finalizar_lazy_loading)

    def finalizar_lazy_loading(self) -> None:
        try:
            self.loading_frame.destroy()
            self.crear_interfaz()
            self.logger.info("✓ Interfaz cargada correctamente con lazy loading")
        except Exception as exc:
            self.logger.error(f"Error al finalizar lazy loading: {exc}")

    def crear_interfaz(self) -> None:
        self.ui_sections.create_main_layout()
        self.ui_sections.create_header()
        self.ui_sections.create_browser_selector()
        self.ui_sections.create_excel_section()
        self.ui_sections.create_action_buttons()
        self.ui_sections.create_logs_area()
        self.ui_sections.create_footer()

    def cambiar_tema(self, tema_id: str) -> None:
        try:
            if self.theme_manager.set_theme(tema_id):
                self.configurar_colores()
                self.actualizar_colores_interfaz()
                for theme_name, btn in self.theme_buttons.items():
                    btn.set_active(theme_name == tema_id)

                theme_names = {
                    "dark": "Modo Oscuro 🌙",
                    "light": "Modo Claro ☀️",
                }
                self.agregar_log(f"✓ Tema cambiado a: {theme_names.get(tema_id, tema_id)}")
        except Exception as exc:
            self.agregar_log(f"✗ Error al cambiar tema: {exc}")

    def actualizar_colores_interfaz(self) -> None:
        DesktopThemeService.apply_runtime_colors(self)

    def _actualizar_labels_recursivo(self, widget) -> None:
        DesktopThemeService._update_labels_recursive(widget, self.COLORES)

    def agregar_log(self, mensaje: str) -> None:
        timestamp = datetime.now().strftime("%H:%M:%S")
        self.text_logs.insert("end", f"[{timestamp}] {mensaje}\n")
        self.text_logs.see("end")

    def seleccionar_excel(self) -> None:
        self.controller.seleccionar_excel()

    def configurar_perfil_navegador(self) -> None:
        self.controller.configurar_perfil_navegador()

    def probar_navegador(self) -> None:
        self.controller.probar_navegador()

    def iniciar_proceso(self) -> None:
        self.controller.iniciar_proceso()

    def notificar_finalizacion(self) -> None:
        def ejecutar_notificacion():
            try:
                try:
                    import winsound

                    winsound.MessageBeep(winsound.MB_ICONASTERISK)
                except Exception as exc:
                    self.logger.warning(f"No se pudo reproducir sonido: {exc}")

                try:
                    self.deiconify()
                except Exception as exc:
                    self.logger.warning(f"No se pudo des-minimizar: {exc}")

                try:
                    self.lift()
                    self.attributes("-topmost", True)
                    self.after(100, lambda: self.attributes("-topmost", False))
                except Exception as exc:
                    self.logger.warning(f"No se pudo traer ventana al frente: {exc}")

                try:
                    self.focus_force()
                except Exception as exc:
                    self.logger.warning(f"No se pudo dar foco: {exc}")

                try:
                    import ctypes

                    hwnd = ctypes.windll.user32.GetParent(self.winfo_id())

                    class FLASHWINFO(ctypes.Structure):
                        _fields_ = [
                            ("cbSize", ctypes.c_uint),
                            ("hwnd", ctypes.c_void_p),
                            ("dwFlags", ctypes.c_uint),
                            ("uCount", ctypes.c_uint),
                            ("dwTimeout", ctypes.c_uint),
                        ]

                    flash_info = FLASHWINFO()
                    flash_info.cbSize = ctypes.sizeof(FLASHWINFO)
                    flash_info.hwnd = hwnd
                    flash_info.dwFlags = 0x0000000F
                    flash_info.uCount = 3
                    flash_info.dwTimeout = 0

                    ctypes.windll.user32.FlashWindowEx(ctypes.byref(flash_info))
                except Exception as exc:
                    self.logger.warning(f"No se pudo hacer parpadeo en taskbar: {exc}")

                self.logger.info("✓ Notificación de finalización ejecutada")
            except Exception as exc:
                self.logger.error(f"Error en notificación de finalización: {exc}")

        self.after(0, ejecutar_notificacion)
