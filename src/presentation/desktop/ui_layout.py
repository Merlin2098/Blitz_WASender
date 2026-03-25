"""
UI Layout Builder - Constructor de secciones de interfaz para WhatsApp Masivo
Funciones que construyen y retornan secciones completas de la interfaz
"""
import customtkinter as ctk
from typing import Callable, Optional, Dict, Any
from .theme_manager import ThemeManager
from .ui_components import (
    ThemedButton, ThemedFrame, ThemedLabel, ThemedEntry,
    ThemedTextBox, ThemedProgressBar, FileSelector, ThemeToggleButton
)


class UIBuilder:
    """Constructor de interfaz de usuario modular"""
    
    def __init__(self, master, theme_manager: ThemeManager):
        """
        Inicializa el constructor de UI
        
        Args:
            master: Ventana principal
            theme_manager: Gestor de temas
        """
        self.master = master
        self.theme_manager = theme_manager
        self.widgets: Dict[str, Any] = {}  # Almacena referencias a widgets
    
    def build_theme_selector(self, on_theme_change: Callable) -> ctk.CTkFrame:
        """
        Construye la barra de selección de temas (esquina superior izquierda)
        
        Args:
            on_theme_change: Callback que se ejecuta al cambiar tema
        
        Returns:
            Frame con los botones de tema
        """
        theme_frame = ctk.CTkFrame(
            self.master,
            fg_color="transparent",
            height=50
        )
        
        # Botón Modo Oscuro (Luna 🌙)
        dark_btn = ThemeToggleButton(
            theme_frame,
            theme_manager=self.theme_manager,
            theme_name="dark",
            icon_text="🌙",
            command=lambda: on_theme_change("dark")
        )
        dark_btn.pack(side="left", padx=2)
        self.widgets['theme_dark_btn'] = dark_btn
        
        # Botón Modo Claro (Sol ☀️)
        light_btn = ThemeToggleButton(
            theme_frame,
            theme_manager=self.theme_manager,
            theme_name="light",
            icon_text="☀️",
            command=lambda: on_theme_change("light")
        )
        light_btn.pack(side="left", padx=2)
        self.widgets['theme_light_btn'] = light_btn
        
        # Botón Modo Daltónico (Círculo cromático 🎨)
        colorblind_btn = ThemeToggleButton(
            theme_frame,
            theme_manager=self.theme_manager,
            theme_name="colorblind",
            icon_text="🎨",
            command=lambda: on_theme_change("colorblind")
        )
        colorblind_btn.pack(side="left", padx=2)
        self.widgets['theme_colorblind_btn'] = colorblind_btn
        
        return theme_frame
    
    def build_header(self) -> ctk.CTkFrame:
        """
        Construye el encabezado de la aplicación
        
        Returns:
            Frame con el título
        """
        header_frame = ThemedFrame(
            self.master,
            theme_manager=self.theme_manager,
            height=80
        )
        
        title = ThemedLabel(
            header_frame,
            theme_manager=self.theme_manager,
            text="📱 WhatsApp Web - Envío Masivo",
            font_size=24,
            bold=True
        )
        title.pack(pady=20)
        self.widgets['title'] = title
        
        return header_frame
    
    def build_file_selectors(self, on_select_excel: Callable, 
                            on_select_driver: Callable) -> ctk.CTkFrame:
        """
        Construye la sección de selectores de archivos
        
        Args:
            on_select_excel: Callback para seleccionar Excel
            on_select_driver: Callback para seleccionar driver
        
        Returns:
            Frame con los selectores
        """
        selectors_frame = ThemedFrame(
            self.master,
            theme_manager=self.theme_manager
        )
        
        # Selector de Excel
        excel_selector = FileSelector(
            selectors_frame,
            theme_manager=self.theme_manager,
            label_text="📊 Archivo Excel:",
            button_text="Examinar",
            command=on_select_excel
        )
        excel_selector.pack(fill="x", padx=20, pady=(15, 10))
        self.widgets['excel_selector'] = excel_selector
        
        # Selector de Driver
        driver_selector = FileSelector(
            selectors_frame,
            theme_manager=self.theme_manager,
            label_text="🔧 Driver del Navegador:",
            button_text="Examinar",
            command=on_select_driver
        )
        driver_selector.pack(fill="x", padx=20, pady=(10, 15))
        self.widgets['driver_selector'] = driver_selector
        
        return selectors_frame
    
    def build_browser_selector(self) -> ctk.CTkFrame:
        """
        Construye el selector de navegador
        
        Returns:
            Frame con el selector de navegador
        """
        browser_frame = ThemedFrame(
            self.master,
            theme_manager=self.theme_manager
        )
        
        label = ThemedLabel(
            browser_frame,
            theme_manager=self.theme_manager,
            text="🌐 Navegador:",
            font_size=11,
            bold=True
        )
        label.pack(anchor="w", padx=15, pady=(10, 5))
        
        # RadioButtons para selección de navegador
        browser_var = ctk.StringVar(value="edge")
        
        radio_frame = ctk.CTkFrame(browser_frame, fg_color="transparent")
        radio_frame.pack(fill="x", padx=15, pady=(0, 10))
        
        edge_radio = ctk.CTkRadioButton(
            radio_frame,
            text="Microsoft Edge",
            variable=browser_var,
            value="edge",
            fg_color=self.theme_manager.get_color("accent"),
            hover_color=self.theme_manager.get_color("accent_hover"),
            text_color=self.theme_manager.get_color("text_primary"),
            font=("Segoe UI", 11)
        )
        edge_radio.pack(side="left", padx=(0, 20))
        
        chrome_radio = ctk.CTkRadioButton(
            radio_frame,
            text="Google Chrome",
            variable=browser_var,
            value="chrome",
            fg_color=self.theme_manager.get_color("accent"),
            hover_color=self.theme_manager.get_color("accent_hover"),
            text_color=self.theme_manager.get_color("text_primary"),
            font=("Segoe UI", 11)
        )
        chrome_radio.pack(side="left")
        
        self.widgets['browser_var'] = browser_var
        self.widgets['browser_label'] = label
        self.widgets['edge_radio'] = edge_radio
        self.widgets['chrome_radio'] = chrome_radio
        
        return browser_frame
    
    def build_validation_section(self) -> ctk.CTkFrame:
        """
        Construye la sección de validación con indicador de estado
        
        Returns:
            Frame con botón de validación y estado
        """
        validation_frame = ThemedFrame(
            self.master,
            theme_manager=self.theme_manager
        )
        
        validate_btn = ThemedButton(
            validation_frame,
            theme_manager=self.theme_manager,
            text="✓ Validar Datos",
            width=200,
            height=40
        )
        validate_btn.pack(pady=15)
        self.widgets['validate_btn'] = validate_btn
        
        status_label = ThemedLabel(
            validation_frame,
            theme_manager=self.theme_manager,
            text="⏳ Esperando validación...",
            font_size=11
        )
        status_label.pack(pady=(0, 15))
        self.widgets['status_label'] = status_label
        
        return validation_frame
    
    def build_progress_section(self) -> ctk.CTkFrame:
        """
        Construye la sección de progreso
        
        Returns:
            Frame con barra de progreso e información
        """
        progress_frame = ThemedFrame(
            self.master,
            theme_manager=self.theme_manager
        )
        
        # Etiqueta de progreso
        progress_label = ThemedLabel(
            progress_frame,
            theme_manager=self.theme_manager,
            text="Progreso del envío:",
            font_size=11,
            bold=True
        )
        progress_label.pack(anchor="w", padx=15, pady=(15, 5))
        self.widgets['progress_label'] = progress_label
        
        # Barra de progreso
        progress_bar = ThemedProgressBar(
            progress_frame,
            theme_manager=self.theme_manager
        )
        progress_bar.set(0)
        progress_bar.pack(fill="x", padx=15, pady=(5, 10))
        self.widgets['progress_bar'] = progress_bar
        
        # Frame para información adicional
        info_frame = ctk.CTkFrame(progress_frame, fg_color="transparent")
        info_frame.pack(fill="x", padx=15, pady=(0, 15))
        
        # Información de envíos
        sent_label = ThemedLabel(
            info_frame,
            theme_manager=self.theme_manager,
            text="Enviados: 0/0",
            font_size=10
        )
        sent_label.pack(side="left")
        self.widgets['sent_label'] = sent_label
        
        # Tiempo restante
        time_label = ThemedLabel(
            info_frame,
            theme_manager=self.theme_manager,
            text="Tiempo restante: --:--",
            font_size=10
        )
        time_label.pack(side="right")
        self.widgets['time_label'] = time_label
        
        return progress_frame
    
    def build_console(self) -> ctk.CTkFrame:
        """
        Construye la consola de logs
        
        Returns:
            Frame con el textbox de consola
        """
        console_frame = ThemedFrame(
            self.master,
            theme_manager=self.theme_manager
        )
        
        console_label = ThemedLabel(
            console_frame,
            theme_manager=self.theme_manager,
            text="📋 Consola de Logs:",
            font_size=11,
            bold=True
        )
        console_label.pack(anchor="w", padx=15, pady=(15, 5))
        self.widgets['console_label'] = console_label
        
        console = ThemedTextBox(
            console_frame,
            theme_manager=self.theme_manager,
            height=200,
            state="disabled"
        )
        console.pack(fill="both", expand=True, padx=15, pady=(5, 15))
        self.widgets['console'] = console
        
        return console_frame
    
    def build_control_buttons(self, on_start: Callable, 
                             on_stop: Callable) -> ctk.CTkFrame:
        """
        Construye los botones de control principales
        
        Args:
            on_start: Callback para iniciar envío
            on_stop: Callback para detener envío
        
        Returns:
            Frame con los botones de control
        """
        buttons_frame = ctk.CTkFrame(
            self.master,
            fg_color="transparent"
        )
        
        # Botón Iniciar
        start_btn = ThemedButton(
            buttons_frame,
            theme_manager=self.theme_manager,
            text="▶ Iniciar Envío",
            command=on_start,
            width=200,
            height=50,
            font=("Segoe UI", 14, "bold")
        )
        start_btn.pack(side="left", padx=10)
        self.widgets['start_btn'] = start_btn
        
        # Botón Detener
        stop_btn = ThemedButton(
            buttons_frame,
            theme_manager=self.theme_manager,
            text="⏹ Detener",
            command=on_stop,
            width=200,
            height=50,
            font=("Segoe UI", 14, "bold"),
            fg_color=self.theme_manager.get_color("error"),
            hover_color="#CC0000",
            state="disabled"
        )
        stop_btn.pack(side="left", padx=10)
        self.widgets['stop_btn'] = stop_btn
        
        return buttons_frame
    
    def get_widget(self, name: str) -> Optional[Any]:
        """
        Obtiene una referencia a un widget por nombre
        
        Args:
            name: Nombre del widget
        
        Returns:
            Widget o None si no existe
        """
        return self.widgets.get(name)
    
    def update_all_themes(self, theme_manager: ThemeManager) -> None:
        """
        Actualiza el tema de todos los widgets creados
        
        Args:
            theme_manager: Nuevo gestor de temas
        """
        self.theme_manager = theme_manager
        
        # Actualizar todos los widgets que tienen el método update_theme
        for widget in self.widgets.values():
            if hasattr(widget, 'update_theme'):
                widget.update_theme(theme_manager)
