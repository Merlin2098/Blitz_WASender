"""
UI Components - Componentes reutilizables para WhatsApp Masivo
Widgets personalizados que se adaptan al tema actual
"""
import customtkinter as ctk
from typing import Callable, Optional
from .theme_manager import ThemeManager


class ThemedButton(ctk.CTkButton):
    """Botón personalizado que se adapta al tema"""
    
    def __init__(self, master, theme_manager: ThemeManager, text: str = "", 
                 command: Optional[Callable] = None, **kwargs):
        """
        Inicializa un botón temático
        
        Args:
            master: Widget padre
            theme_manager: Gestor de temas
            text: Texto del botón
            command: Función a ejecutar al hacer clic
            **kwargs: Argumentos adicionales para CTkButton
        """
        self.theme_manager = theme_manager
        
        # Configuración por defecto basada en el tema
        default_config = {
            "fg_color": self.theme_manager.get_color("accent"),
            "hover_color": self.theme_manager.get_color("accent_hover"),
            "text_color": self.theme_manager.get_color("text_primary"),
            "border_width": 0,
            "corner_radius": 8,
            "font": ("Segoe UI", 12, "bold")
        }
        
        # Mezclar configuración por defecto con kwargs personalizados
        default_config.update(kwargs)
        
        super().__init__(master, text=text, command=command, **default_config)
    
    def update_theme(self, theme_manager: ThemeManager) -> None:
        """Actualiza los colores del botón según el nuevo tema"""
        self.theme_manager = theme_manager
        self.configure(
            fg_color=self.theme_manager.get_color("accent"),
            hover_color=self.theme_manager.get_color("accent_hover"),
            text_color=self.theme_manager.get_color("text_primary")
        )


class ThemedFrame(ctk.CTkFrame):
    """Frame personalizado que se adapta al tema"""
    
    def __init__(self, master, theme_manager: ThemeManager, **kwargs):
        """
        Inicializa un frame temático
        
        Args:
            master: Widget padre
            theme_manager: Gestor de temas
            **kwargs: Argumentos adicionales para CTkFrame
        """
        self.theme_manager = theme_manager
        
        default_config = {
            "fg_color": self.theme_manager.get_color("bg_secondary"),
            "corner_radius": 10,
            "border_width": 1,
            "border_color": self.theme_manager.get_color("border")
        }
        
        default_config.update(kwargs)
        super().__init__(master, **default_config)
    
    def update_theme(self, theme_manager: ThemeManager) -> None:
        """Actualiza los colores del frame según el nuevo tema"""
        self.theme_manager = theme_manager
        self.configure(
            fg_color=self.theme_manager.get_color("bg_secondary"),
            border_color=self.theme_manager.get_color("border")
        )


class ThemedLabel(ctk.CTkLabel):
    """Label personalizado que se adapta al tema"""
    
    def __init__(self, master, theme_manager: ThemeManager, text: str = "", 
                 font_size: int = 12, bold: bool = False, **kwargs):
        """
        Inicializa un label temático
        
        Args:
            master: Widget padre
            theme_manager: Gestor de temas
            text: Texto del label
            font_size: Tamaño de fuente
            bold: Si el texto debe ser negrita
            **kwargs: Argumentos adicionales para CTkLabel
        """
        self.theme_manager = theme_manager
        
        font_weight = "bold" if bold else "normal"
        default_config = {
            "text_color": self.theme_manager.get_color("text_primary"),
            "font": ("Segoe UI", font_size, font_weight)
        }
        
        default_config.update(kwargs)
        super().__init__(master, text=text, **default_config)
    
    def update_theme(self, theme_manager: ThemeManager) -> None:
        """Actualiza los colores del label según el nuevo tema"""
        self.theme_manager = theme_manager
        self.configure(text_color=self.theme_manager.get_color("text_primary"))


class ThemedEntry(ctk.CTkEntry):
    """Entry personalizado que se adapta al tema"""
    
    def __init__(self, master, theme_manager: ThemeManager, placeholder: str = "", **kwargs):
        """
        Inicializa un entry temático
        
        Args:
            master: Widget padre
            theme_manager: Gestor de temas
            placeholder: Texto de marcador de posición
            **kwargs: Argumentos adicionales para CTkEntry
        """
        self.theme_manager = theme_manager
        
        default_config = {
            "fg_color": self.theme_manager.get_color("bg_tertiary"),
            "border_color": self.theme_manager.get_color("border"),
            "text_color": self.theme_manager.get_color("text_primary"),
            "placeholder_text": placeholder,
            "placeholder_text_color": self.theme_manager.get_color("text_disabled"),
            "corner_radius": 8,
            "border_width": 1,
            "font": ("Segoe UI", 11)
        }
        
        default_config.update(kwargs)
        super().__init__(master, **default_config)
    
    def update_theme(self, theme_manager: ThemeManager) -> None:
        """Actualiza los colores del entry según el nuevo tema"""
        self.theme_manager = theme_manager
        self.configure(
            fg_color=self.theme_manager.get_color("bg_tertiary"),
            border_color=self.theme_manager.get_color("border"),
            text_color=self.theme_manager.get_color("text_primary"),
            placeholder_text_color=self.theme_manager.get_color("text_disabled")
        )


class ThemedTextBox(ctk.CTkTextbox):
    """TextBox personalizado que se adapta al tema (para consola de logs)"""
    
    def __init__(self, master, theme_manager: ThemeManager, **kwargs):
        """
        Inicializa un textbox temático
        
        Args:
            master: Widget padre
            theme_manager: Gestor de temas
            **kwargs: Argumentos adicionales para CTkTextbox
        """
        self.theme_manager = theme_manager
        
        default_config = {
            "fg_color": self.theme_manager.get_color("console_bg"),
            "text_color": self.theme_manager.get_color("console_text"),
            "border_width": 1,
            "border_color": self.theme_manager.get_color("border"),
            "corner_radius": 8,
            "font": ("Consolas", 10),
            "wrap": "word"
        }
        
        default_config.update(kwargs)
        super().__init__(master, **default_config)
    
    def update_theme(self, theme_manager: ThemeManager) -> None:
        """Actualiza los colores del textbox según el nuevo tema"""
        self.theme_manager = theme_manager
        self.configure(
            fg_color=self.theme_manager.get_color("console_bg"),
            text_color=self.theme_manager.get_color("console_text"),
            border_color=self.theme_manager.get_color("border")
        )


class ThemedProgressBar(ctk.CTkProgressBar):
    """Barra de progreso personalizada que se adapta al tema"""
    
    def __init__(self, master, theme_manager: ThemeManager, **kwargs):
        """
        Inicializa una barra de progreso temática
        
        Args:
            master: Widget padre
            theme_manager: Gestor de temas
            **kwargs: Argumentos adicionales para CTkProgressBar
        """
        self.theme_manager = theme_manager
        
        default_config = {
            "progress_color": self.theme_manager.get_color("accent"),
            "fg_color": self.theme_manager.get_color("bg_tertiary"),
            "corner_radius": 8,
            "height": 20,
            "border_width": 0
        }
        
        default_config.update(kwargs)
        super().__init__(master, **default_config)
    
    def update_theme(self, theme_manager: ThemeManager) -> None:
        """Actualiza los colores de la barra según el nuevo tema"""
        self.theme_manager = theme_manager
        self.configure(
            progress_color=self.theme_manager.get_color("accent"),
            fg_color=self.theme_manager.get_color("bg_tertiary")
        )


class FileSelector(ctk.CTkFrame):
    """Componente compuesto para selección de archivos"""
    
    def __init__(self, master, theme_manager: ThemeManager, label_text: str, 
                 button_text: str = "Seleccionar", command: Optional[Callable] = None):
        """
        Inicializa un selector de archivos
        
        Args:
            master: Widget padre
            theme_manager: Gestor de temas
            label_text: Texto de la etiqueta
            button_text: Texto del botón
            command: Función a ejecutar al hacer clic
        """
        super().__init__(
            master,
            fg_color=theme_manager.get_color("bg_secondary"),
            corner_radius=10,
            border_width=1,
            border_color=theme_manager.get_color("border")
        )
        
        self.theme_manager = theme_manager
        
        # Label
        self.label = ThemedLabel(
            self, 
            theme_manager=theme_manager,
            text=label_text,
            font_size=11,
            bold=True
        )
        self.label.pack(anchor="w", padx=15, pady=(10, 5))
        
        # Frame para entry y botón
        self.input_frame = ctk.CTkFrame(self, fg_color="transparent")
        self.input_frame.pack(fill="x", padx=15, pady=(0, 10))
        
        # Entry
        self.entry = ThemedEntry(
            self.input_frame,
            theme_manager=theme_manager,
            placeholder="Ningún archivo seleccionado"
        )
        self.entry.pack(side="left", fill="x", expand=True, padx=(0, 10))
        
        # Botón
        self.button = ThemedButton(
            self.input_frame,
            theme_manager=theme_manager,
            text=button_text,
            command=command,
            width=120
        )
        self.button.pack(side="right")
    
    def get_path(self) -> str:
        """Obtiene la ruta del archivo seleccionado"""
        return self.entry.get()
    
    def set_path(self, path: str) -> None:
        """Establece la ruta en el entry"""
        self.entry.delete(0, "end")
        self.entry.insert(0, path)
    
    def update_theme(self, theme_manager: ThemeManager) -> None:
        """Actualiza el tema de todos los componentes"""
        self.theme_manager = theme_manager
        self.configure(
            fg_color=theme_manager.get_color("bg_secondary"),
            border_color=theme_manager.get_color("border")
        )
        self.label.update_theme(theme_manager)
        self.entry.update_theme(theme_manager)
        self.button.update_theme(theme_manager)


class ThemeToggleButton(ctk.CTkButton):
    """Botón especializado para cambio de tema con iconos"""
    
    def __init__(self, master, theme_manager: ThemeManager, theme_name: str,
                 icon_text: str, command: Optional[Callable] = None):
        """
        Inicializa un botón de cambio de tema
        
        Args:
            master: Widget padre
            theme_manager: Gestor de temas
            theme_name: Nombre del tema ('dark', 'light', 'colorblind')
            icon_text: Texto del icono (emoji o símbolo)
            command: Función a ejecutar al hacer clic
        """
        self.theme_manager = theme_manager
        self.theme_name = theme_name
        
        # Determinar si este tema está activo
        is_active = theme_manager.get_current_theme_name() == theme_name
        
        super().__init__(
            master,
            text=icon_text,
            command=command,
            width=40,
            height=40,
            corner_radius=8,
            fg_color=theme_manager.get_color("accent") if is_active else theme_manager.get_color("bg_tertiary"),
            hover_color=theme_manager.get_color("accent_hover"),
            text_color=theme_manager.get_color("text_primary"),
            font=("Segoe UI", 18),
            border_width=2 if is_active else 1,
            border_color=theme_manager.get_color("accent") if is_active else theme_manager.get_color("border")
        )
    
    def set_active(self, is_active: bool) -> None:
        """Marca este botón como activo o inactivo"""
        self.configure(
            fg_color=self.theme_manager.get_color("accent") if is_active else self.theme_manager.get_color("bg_tertiary"),
            border_width=2 if is_active else 1,
            border_color=self.theme_manager.get_color("accent") if is_active else self.theme_manager.get_color("border")
        )
    
    def update_theme(self, theme_manager: ThemeManager) -> None:
        """Actualiza el tema del botón"""
        self.theme_manager = theme_manager
        is_active = theme_manager.get_current_theme_name() == self.theme_name
        self.set_active(is_active)
