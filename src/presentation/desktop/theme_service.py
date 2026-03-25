from __future__ import annotations

import customtkinter as ctk


class DesktopThemeService:
    """
    Adaptador de temas para la interfaz desktop.
    """

    @staticmethod
    def build_palette(theme_manager) -> dict:
        return {
            "bg_principal": theme_manager.get_color("bg_primary"),
            "bg_secundario": theme_manager.get_color("bg_secondary"),
            "bg_input": theme_manager.get_color("bg_tertiary"),
            "turquesa": theme_manager.get_color("accent"),
            "turquesa_hover": theme_manager.get_color("accent_hover"),
            "gris_claro": theme_manager.get_color("text_primary"),
            "gris_medio": theme_manager.get_color("text_secondary"),
            "verde": theme_manager.get_color("success"),
            "rojo": theme_manager.get_color("error"),
            "amarillo": theme_manager.get_color("warning"),
        }

    @classmethod
    def configure_window(cls, app) -> None:
        app.COLORES = cls.build_palette(app.theme_manager)
        app.configure(fg_color=app.COLORES["bg_principal"])

    @classmethod
    def apply_runtime_colors(cls, app) -> None:
        try:
            cls.configure_window(app)

            if hasattr(app, "main_frame"):
                app.main_frame.configure(fg_color=app.COLORES["bg_principal"])

            if hasattr(app, "entry_excel"):
                app.entry_excel.configure(
                    fg_color=app.COLORES["bg_input"],
                    border_color=app.COLORES["turquesa"],
                    text_color=app.COLORES["gris_claro"],
                )

            if hasattr(app, "combo_navegador"):
                app.combo_navegador.configure(
                    fg_color=app.COLORES["bg_input"],
                    button_color=app.COLORES["turquesa"],
                    button_hover_color=app.COLORES["turquesa_hover"],
                    border_color=app.COLORES["turquesa"],
                    text_color=app.COLORES["gris_claro"],
                )

            if hasattr(app, "btn_configurar_perfil"):
                app.btn_configurar_perfil.configure(
                    fg_color=app.COLORES["turquesa"],
                    hover_color=app.COLORES["turquesa_hover"],
                    text_color="white",
                )

            if hasattr(app, "btn_probar_navegador"):
                app.btn_probar_navegador.configure(
                    fg_color=app.COLORES["verde"],
                    hover_color="#1a8754",
                    text_color="white",
                )

            if hasattr(app, "btn_iniciar"):
                app.btn_iniciar.configure(
                    fg_color=app.COLORES["verde"],
                    hover_color="#1a8754",
                    text_color="white",
                )

            if hasattr(app, "text_logs"):
                app.text_logs.configure(
                    fg_color=app.COLORES["bg_principal"],
                    text_color=app.COLORES["gris_claro"],
                )

            if hasattr(app, "label_info"):
                app.label_info.configure(text_color=app.COLORES["gris_medio"])

            if hasattr(app, "main_frame"):
                cls._update_labels_recursive(app.main_frame, app.COLORES)

        except Exception as exc:
            print(f"Error al actualizar colores: {exc}")

    @classmethod
    def _update_labels_recursive(cls, widget, colors) -> None:
        try:
            if isinstance(widget, ctk.CTkLabel):
                current_color = widget.cget("text_color")
                if current_color in ["white", "#FFFFFF", "#CCCCCC", "#666666", "gray", "black", "#000000"]:
                    widget.configure(text_color=colors["gris_claro"])

            if hasattr(widget, "winfo_children"):
                for child in widget.winfo_children():
                    cls._update_labels_recursive(child, colors)
        except Exception:
            pass
