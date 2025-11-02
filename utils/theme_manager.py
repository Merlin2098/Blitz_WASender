import json
import os
import sys
from typing import Dict, List, Optional


def obtener_ruta_base():
    """
    Retorna la ruta base según el entorno:
    - Si es .exe (PyInstaller): carpeta donde está el ejecutable
    - Si es Python: raíz del proyecto
    
    Returns:
        str: Ruta base absoluta
    """
    if getattr(sys, 'frozen', False):
        # Ejecutándose desde PyInstaller (.exe)
        return os.path.dirname(sys.executable)
    else:
        # Ejecutándose desde Python (subir un nivel desde utils/ hasta raíz del proyecto)
        return os.path.dirname(os.path.dirname(os.path.abspath(__file__)))


def obtener_ruta_recurso(nombre_archivo):
    """
    Retorna la ruta correcta para archivos empaquetados o en desarrollo.
    Busca el recurso dentro de la carpeta 'recursos' del proyecto si no se encuentra en la raíz.
    """
    posibles_rutas = []

    # 1️⃣ Si está empaquetado con PyInstaller
    if getattr(sys, 'frozen', False) and hasattr(sys, '_MEIPASS'):
        posibles_rutas.append(os.path.join(sys._MEIPASS, nombre_archivo))
        posibles_rutas.append(os.path.join(sys._MEIPASS, "recursos", nombre_archivo))

    # 2️⃣ En el directorio base del script o ejecutable
    ruta_base = obtener_ruta_base()
    posibles_rutas.extend([
        os.path.join(ruta_base, nombre_archivo),
        os.path.join(ruta_base, "recursos", nombre_archivo)
    ])

    # 3️⃣ En el directorio actual (por compatibilidad)
    posibles_rutas.append(os.path.join(os.getcwd(), nombre_archivo))
    posibles_rutas.append(os.path.join(os.getcwd(), "recursos", nombre_archivo))

    for ruta in posibles_rutas:
        if os.path.exists(ruta):
            return ruta

    print(f"⚠️ No se encontró el recurso: {nombre_archivo}")
    return None


class ThemeManager:
    """Gestor centralizado de temas de la aplicación"""
    
    def __init__(self, themes_file: str = "themes.json", default_theme: str = "dark"):
        """
        Inicializa el gestor de temas
        
        Args:
            themes_file: Nombre del archivo JSON de temas
            default_theme: Tema por defecto a cargar
        """
        self.themes_file = themes_file
        self.themes: Dict = {}
        self.current_theme: str = default_theme
        self.current_colors: Dict = {}
        
        # Cargar temas desde el archivo JSON
        self._load_themes()
        
        # Establecer tema por defecto
        self.set_theme(default_theme)
    
    def _load_themes(self) -> None:
        """Carga los temas desde el archivo JSON"""
        try:
            ruta_tema = obtener_ruta_recurso(self.themes_file)
            if not ruta_tema or not os.path.exists(ruta_tema):
                raise FileNotFoundError(f"No se encontró el archivo de temas en 'recursos/' o ruta base.")

            with open(ruta_tema, 'r', encoding='utf-8') as f:
                themes_data = json.load(f)

            print(f"✓ themes.json cargado desde: {ruta_tema}")
            self.themes = themes_data

        except FileNotFoundError as e:
            print(f"⚠️ Error: {e}")
            self._load_fallback_theme()
        except json.JSONDecodeError as e:
            print(f"⚠️ Error al parsear JSON: {e}")
            self._load_fallback_theme()
    
    def _load_fallback_theme(self) -> None:
        """Carga un tema de respaldo en caso de error"""
        self.themes = {
            "dark": {
                "name": "Modo Oscuro (fallback)",
                "bg_primary": "#1a1a1a",
                "bg_secondary": "#2b2b2b",
                "bg_tertiary": "#3d3d3d",
                "accent": "#00CED1",
                "accent_hover": "#00B8BA",
                "accent_disabled": "#006B6D",
                "text_primary": "#FFFFFF",
                "text_secondary": "#CCCCCC",
                "text_disabled": "#666666",
                "success": "#00FF7F",
                "warning": "#FFA500",
                "error": "#FF4444",
                "border": "#404040",
                "console_bg": "#1a1a1a",
                "console_text": "#00CED1"
            }
        }
    
    def set_theme(self, theme_name: str) -> bool:
        """Cambia el tema actual"""
        if theme_name in self.themes:
            self.current_theme = theme_name
            self.current_colors = self.themes[theme_name]
            return True
        else:
            print(f"⚠️ Tema '{theme_name}' no encontrado. Usando tema actual: {self.current_theme}")
            return False
    
    def get_color(self, key: str, fallback: str = "#FFFFFF") -> str:
        """Obtiene un color del tema actual"""
        return self.current_colors.get(key, fallback)
    
    def get_all_colors(self) -> Dict[str, str]:
        """Obtiene todos los colores del tema actual"""
        return self.current_colors.copy()
    
    def get_available_themes(self) -> List[str]:
        """Obtiene la lista de temas disponibles"""
        return list(self.themes.keys())
    
    def get_theme_info(self, theme_name: str) -> Optional[Dict]:
        """Obtiene la información completa de un tema"""
        return self.themes.get(theme_name)
    
    def get_current_theme_name(self) -> str:
        """Obtiene el nombre del tema actual"""
        return self.current_theme
    
    def reload_themes(self) -> None:
        """Recarga los temas desde el archivo JSON"""
        self._load_themes()
        self.set_theme(self.current_theme)


# Instancia global
_theme_manager_instance: Optional[ThemeManager] = None


def get_theme_manager(themes_file: str = "themes.json", default_theme: str = "dark") -> ThemeManager:
    """Obtiene la instancia singleton del ThemeManager"""
    global _theme_manager_instance
    if _theme_manager_instance is None:
        _theme_manager_instance = ThemeManager(themes_file, default_theme)
    return _theme_manager_instance
