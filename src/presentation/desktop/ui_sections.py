from __future__ import annotations

import customtkinter as ctk

from .ui_components import ThemeToggleButton


class DesktopUISections:
    """
    Builder parcial de secciones de la GUI principal.
    """

    def __init__(self, app):
        self.app = app

    def create_main_layout(self) -> None:
        self.app.main_frame = ctk.CTkScrollableFrame(
            self.app,
            fg_color=self.app.COLORES["bg_principal"],
        )
        self.app.main_frame.pack(fill="both", expand=True, padx=20, pady=20)

    def create_header(self) -> None:
        app = self.app
        header_frame = ctk.CTkFrame(app.main_frame, fg_color="transparent")
        header_frame.pack(fill="x", pady=(0, 20))

        title_frame = ctk.CTkFrame(header_frame, fg_color="transparent")
        title_frame.pack(side="left", fill="x", expand=True)

        titulo = ctk.CTkLabel(
            title_frame,
            text="📱 WhatsApp Web - Envío Masivo",
            font=("Segoe UI", 28, "bold"),
            text_color=app.COLORES["turquesa"],
        )
        titulo.pack(anchor="w")

        subtitulo = ctk.CTkLabel(
            title_frame,
            text="Versión 2.3 - Sprint 3.1 | Selenium Manager + Gestión de Perfiles",
            font=("Segoe UI", 12),
            text_color=app.COLORES["gris_medio"],
        )
        subtitulo.pack(anchor="w", pady=(5, 0))

        theme_frame = ctk.CTkFrame(header_frame, fg_color="transparent")
        theme_frame.pack(side="right", padx=(10, 0))

        theme_label = ctk.CTkLabel(
            theme_frame,
            text="Temas:",
            font=("Segoe UI", 11),
            text_color=app.COLORES["gris_medio"],
        )
        theme_label.pack(pady=(0, 5))

        buttons_container = ctk.CTkFrame(theme_frame, fg_color="transparent")
        buttons_container.pack()

        dark_btn = ThemeToggleButton(
            buttons_container,
            theme_manager=app.theme_manager,
            theme_name="dark",
            icon_text="🌙",
            command=lambda: app.cambiar_tema("dark"),
        )
        dark_btn.pack(side="left", padx=2)
        app.theme_buttons["dark"] = dark_btn

        light_btn = ThemeToggleButton(
            buttons_container,
            theme_manager=app.theme_manager,
            theme_name="light",
            icon_text="☀️",
            command=lambda: app.cambiar_tema("light"),
        )
        light_btn.pack(side="left", padx=2)
        app.theme_buttons["light"] = light_btn

    def create_browser_selector(self) -> None:
        app = self.app
        frame = ctk.CTkFrame(app.main_frame, fg_color=app.COLORES["bg_secundario"], corner_radius=10)
        frame.pack(fill="x", pady=(0, 15))

        inner_frame = ctk.CTkFrame(frame, fg_color="transparent")
        inner_frame.pack(fill="x", padx=20, pady=15)

        label = ctk.CTkLabel(
            inner_frame,
            text="🌐 Navegador:",
            font=("Segoe UI", 14, "bold"),
            text_color=app.COLORES["gris_claro"],
        )
        label.pack(side="left", padx=(0, 15))

        app.combo_navegador = ctk.CTkComboBox(
            inner_frame,
            values=["Edge", "Chrome", "Firefox"],
            width=150,
            font=("Segoe UI", 12),
            dropdown_font=("Segoe UI", 11),
            fg_color=app.COLORES["bg_input"],
            button_color=app.COLORES["turquesa"],
            button_hover_color=app.COLORES["turquesa_hover"],
            border_color=app.COLORES["turquesa"],
            state="readonly",
        )
        app.combo_navegador.set("Edge")
        app.combo_navegador.pack(side="left", padx=(0, 10))

        app.btn_configurar_perfil = ctk.CTkButton(
            inner_frame,
            text="⚙️ Configurar Perfil",
            font=("Segoe UI", 12),
            fg_color=app.COLORES["turquesa"],
            hover_color=app.COLORES["turquesa_hover"],
            text_color="white",
            corner_radius=8,
            width=150,
            height=32,
            command=app.configurar_perfil_navegador,
        )
        app.btn_configurar_perfil.pack(side="left", padx=(0, 10))

        app.btn_probar_navegador = ctk.CTkButton(
            inner_frame,
            text="🌐 Probar Navegador",
            font=("Segoe UI", 12),
            fg_color=app.COLORES["verde"],
            hover_color="#1a8754",
            text_color="white",
            corner_radius=8,
            width=150,
            height=32,
            command=app.probar_navegador,
        )
        app.btn_probar_navegador.pack(side="left")

    def create_excel_section(self) -> None:
        app = self.app
        frame = ctk.CTkFrame(app.main_frame, fg_color=app.COLORES["bg_secundario"], corner_radius=10)
        frame.pack(fill="x", pady=(0, 15))

        inner_frame = ctk.CTkFrame(frame, fg_color="transparent")
        inner_frame.pack(fill="x", padx=20, pady=15)

        label = ctk.CTkLabel(
            inner_frame,
            text="📂 Archivo Excel:",
            font=("Segoe UI", 14, "bold"),
            text_color=app.COLORES["gris_claro"],
        )
        label.pack(anchor="w", pady=(0, 10))

        input_frame = ctk.CTkFrame(inner_frame, fg_color="transparent")
        input_frame.pack(fill="x")

        app.entry_excel = ctk.CTkEntry(
            input_frame,
            placeholder_text="Selecciona un archivo Excel (.xlsx)",
            font=("Segoe UI", 12),
            height=40,
            fg_color=app.COLORES["bg_input"],
            border_color=app.COLORES["turquesa"],
        )
        app.entry_excel.pack(side="left", fill="x", expand=True, padx=(0, 10))

        btn_examinar = ctk.CTkButton(
            input_frame,
            text="📁 Examinar",
            font=("Segoe UI", 12, "bold"),
            fg_color=app.COLORES["turquesa"],
            hover_color=app.COLORES["turquesa_hover"],
            text_color="white",
            corner_radius=8,
            width=120,
            height=40,
            command=app.seleccionar_excel,
        )
        btn_examinar.pack(side="left")

    def create_action_buttons(self) -> None:
        app = self.app
        frame = ctk.CTkFrame(app.main_frame, fg_color="transparent")
        frame.pack(fill="x", pady=(0, 15))

        app.btn_iniciar = ctk.CTkButton(
            frame,
            text="▶️ INICIAR ENVÍO MASIVO",
            font=("Segoe UI", 16, "bold"),
            fg_color=app.COLORES["verde"],
            hover_color="#1a8754",
            text_color="white",
            corner_radius=10,
            height=50,
            command=app.iniciar_proceso,
        )
        app.btn_iniciar.pack(fill="x", pady=(0, 10))

        app.label_info = ctk.CTkLabel(
            frame,
            text="ℹ️ Carga un archivo Excel y selecciona un navegador para comenzar",
            font=("Segoe UI", 11),
            text_color=app.COLORES["gris_medio"],
        )
        app.label_info.pack()

    def create_logs_area(self) -> None:
        app = self.app
        frame = ctk.CTkFrame(app.main_frame, fg_color=app.COLORES["bg_secundario"], corner_radius=10)
        frame.pack(fill="both", expand=True, pady=(0, 15))

        inner_frame = ctk.CTkFrame(frame, fg_color="transparent")
        inner_frame.pack(fill="both", expand=True, padx=20, pady=15)

        label = ctk.CTkLabel(
            inner_frame,
            text="📋 Registro de Actividad:",
            font=("Segoe UI", 14, "bold"),
            text_color=app.COLORES["gris_claro"],
        )
        label.pack(anchor="w", pady=(0, 10))

        app.text_logs = ctk.CTkTextbox(
            inner_frame,
            height=250,
            font=("Consolas", 11),
            fg_color=app.COLORES["bg_principal"],
            text_color=app.COLORES["gris_claro"],
            border_width=1,
            border_color=app.COLORES["turquesa"],
            corner_radius=8,
        )
        app.text_logs.pack(fill="both", expand=True)

    def create_footer(self) -> None:
        app = self.app
        footer = ctk.CTkLabel(
            app.main_frame,
            text="© 2025 Blitz WaSenderBot. 🚀 Solución de mensajería masiva automatizada. Desarrollado por Ricardo Uculmana Quispe con Python + Selenium",
            font=("Segoe UI", 12),
            text_color=app.COLORES["gris_medio"],
        )
        footer.pack(pady=(10, 0))
