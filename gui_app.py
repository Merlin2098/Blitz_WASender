"""
Aplicación GUI para envío masivo de mensajes por WhatsApp Web
Versión 2.3 - Gestión automática de drivers con Selenium Manager
Sprint 3.1 - Gestión de perfiles de navegador
"""

import customtkinter as ctk
import os
import sys
import time
import threading
from pathlib import Path
from tkinter import filedialog, messagebox
from datetime import datetime
import psutil  # SPRINT 3: Detección de batería

# Importar módulos propios
from utils.theme_manager import get_theme_manager
from utils.ui_components import ThemeToggleButton
from utils.logger import crear_logger, log_separador, log_seccion, cerrar_logger
from utils.excel_handler import leer_mensajes, leer_contactos, procesar_datos, generar_reporte
from utils.whatsapp_sender import WhatsAppSender

# Importar Selenium
from selenium import webdriver
from selenium.webdriver.edge.options import Options as EdgeOptions
from selenium.webdriver.chrome.options import Options as ChromeOptions
from selenium.webdriver.firefox.options import Options as FirefoxOptions


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
        # Ejecutándose desde Python
        return os.path.dirname(os.path.abspath(__file__))

def obtener_ruta_recurso(nombre_archivo):
    """
    Retorna la ruta correcta para archivos empaquetados con PyInstaller o durante el desarrollo.
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

    # Buscar la primera ruta existente
    for ruta in posibles_rutas:
        if os.path.exists(ruta):
            return ruta

    print(f"⚠️ No se encontró el recurso: {nombre_archivo}")
    return None


def obtener_ruta_perfiles(navegador):
    """
    Retorna la ruta de la carpeta de perfiles para el navegador especificado.
    
    Args:
        navegador (str): Nombre del navegador ('edge', 'chrome', 'firefox')
    
    Returns:
        str: Ruta completa a la carpeta de perfil del navegador
    """
    ruta_base = obtener_ruta_base()
    ruta_perfiles = os.path.join(ruta_base, 'perfiles', navegador.lower())
    
    # Crear carpeta si no existe
    if not os.path.exists(ruta_perfiles):
        os.makedirs(ruta_perfiles)
    
    return ruta_perfiles


# Configuración de tema CustomTkinter
ctk.set_appearance_mode("dark")
ctk.set_default_color_theme("blue")


class WhatsAppGUI(ctk.CTk):
    """Clase principal de la interfaz gráfica."""
    
    def __init__(self):
        super().__init__()
        
        # Configuración de la ventana
        self.title("Blitz WaSender: Herramienta de Envío Masivo de Mensajes (v2.3)")
        self.geometry("900x750")
        self.minsize(800, 650)
        
        # SPRINT 3: Maximizar ventana y forzar foco al iniciar
        self.state('zoomed')  # Maximizar ventana (Windows)
        
        # Configurar color de barra de título (gris claro fijo)
        self.after(100, lambda: self.wm_attributes("-alpha", 0.99))
        self.after(200, lambda: self.wm_attributes("-alpha", 1.0))
        try:
            # Intentar establecer color de barra de título en Windows
            import ctypes
            ctypes.windll.dwmapi.DwmSetWindowAttribute(
                ctypes.windll.user32.GetParent(self.winfo_id()),
                35,  # DWMWA_CAPTION_COLOR
                ctypes.byref(ctypes.c_int(0xE0E0E0)),  # Color #E0E0E0 en formato BGR
                ctypes.sizeof(ctypes.c_int)
            )
        except:
            pass  # Si falla, continuar sin cambiar el color
        
        # Intentar establecer el ícono (si existe)
        try:
            icon_path = obtener_ruta_recurso("app_icon.ico")
            if icon_path:
                self.iconbitmap(icon_path)
                print(f"✓ Ícono cargado desde: {icon_path}")
            else:
                print("⚠️ No se encontró app_icon.ico")
        except Exception as e:
            print(f"✗ No se pudo cargar el ícono: {e}")
        
        # SPRINT 3: Forzar foco y traer ventana al frente al inicializar
        self.lift()
        self.focus_force()
        self.attributes('-topmost', True)
        self.after(300, lambda: self.attributes('-topmost', False))
        
        # Variables
        self.ruta_excel = None
        self.navegador_seleccionado = "Edge"  # Por defecto
        self.mensajes_dict = None
        self.contactos_list = None
        self.datos_procesados = None
        self.logger = None
        self.driver = None
        self.enviando = False
        self.cancelar_envio = False
        
        # Rutas del proyecto (dinámicas)
        ruta_base = obtener_ruta_base()
        self.BASE_DIR = ruta_base
        self.LOGS_DIR = os.path.join(ruta_base, "logs")
        
        # Crear carpetas necesarias
        self.crear_carpetas()
        
        # Crear logger
        self.logger = crear_logger("gui_app", self.LOGS_DIR)
        
        # Inicializar sistema de temas
        self.theme_manager = get_theme_manager(default_theme="dark")
        self.theme_buttons = {}
        
        # Configurar colores desde el tema
        self.configurar_colores()
        
        # SPRINT 3: Lazy loading de interfaz
        self.iniciar_lazy_loading()
    
    
    def crear_carpetas(self):
        """Crea las carpetas necesarias si no existen."""
        if not os.path.exists(self.LOGS_DIR):
            os.makedirs(self.LOGS_DIR)
    
    
    def configurar_colores(self):
        """Define la paleta de colores desde el sistema de temas."""
        self.COLORES = {
            'bg_principal': self.theme_manager.get_color('bg_primary'),
            'bg_secundario': self.theme_manager.get_color('bg_secondary'),
            'bg_input': self.theme_manager.get_color('bg_tertiary'),
            'turquesa': self.theme_manager.get_color('accent'),
            'turquesa_hover': self.theme_manager.get_color('accent_hover'),
            'gris_claro': self.theme_manager.get_color('text_primary'),
            'gris_medio': self.theme_manager.get_color('text_secondary'),
            'verde': self.theme_manager.get_color('success'),
            'rojo': self.theme_manager.get_color('error'),
            'amarillo': self.theme_manager.get_color('warning')
        }
        
        # Actualizar color de fondo de la ventana
        self.configure(fg_color=self.COLORES['bg_principal'])
    
    # =====================================
    # SPRINT 3: MÉTODOS NUEVOS
    # =====================================
    
    def iniciar_lazy_loading(self):
        """
        Inicia el proceso de carga progresiva de la interfaz.
        
        SPRINT 3: Carga en 3 fases con barra de progreso.
        """
        # Crear frame de loading
        self.loading_frame = ctk.CTkFrame(self, fg_color=self.COLORES['bg_principal'])
        self.loading_frame.pack(fill='both', expand=True)
        
        # Label de carga
        self.loading_label = ctk.CTkLabel(
            self.loading_frame,
            text="Cargando aplicación...",
            font=("Segoe UI", 20, "bold"),
            text_color=self.COLORES['turquesa']
        )
        self.loading_label.pack(pady=(250, 20))
        
        # Barra de progreso
        self.loading_progress = ctk.CTkProgressBar(
            self.loading_frame,
            width=400,
            height=8,
            corner_radius=4,
            progress_color=self.COLORES['turquesa']
        )
        self.loading_progress.pack(pady=10)
        self.loading_progress.set(0)
        
        # Label de estado
        self.loading_status = ctk.CTkLabel(
            self.loading_frame,
            text="Iniciando...",
            font=("Segoe UI", 12),
            text_color=self.COLORES['gris_medio']
        )
        self.loading_status.pack(pady=10)
        
        # Iniciar carga en thread separado
        threading.Thread(target=self.ejecutar_lazy_loading, daemon=True).start()
    
    
    def ejecutar_lazy_loading(self):
        """
        Ejecuta las 3 fases de carga progresiva de la interfaz.
        
        SPRINT 3: Lazy loading optimizado.
        """
        try:
            # FASE 1: Cargar estructura básica (33%)
            self.loading_status.configure(text="Cargando estructura básica...")
            self.loading_progress.set(0.33)
            time.sleep(0.3)
            
            # FASE 2: Cargar componentes principales (66%)
            self.loading_status.configure(text="Cargando componentes...")
            self.loading_progress.set(0.66)
            time.sleep(0.3)
            
            # FASE 3: Finalizar interfaz (100%)
            self.loading_status.configure(text="Finalizando...")
            self.loading_progress.set(1.0)
            time.sleep(0.3)
            
            # Destruir frame de loading y crear interfaz real
            self.after(0, self.finalizar_lazy_loading)
        
        except Exception as e:
            self.logger.error(f"Error en lazy loading: {e}")
            self.after(0, self.finalizar_lazy_loading)
    
    
    def finalizar_lazy_loading(self):
        """
        Finaliza el lazy loading destruyendo el frame de carga y creando la interfaz real.
        
        SPRINT 3: Este método se ejecuta en el thread principal de tkinter.
        """
        try:
            # Destruir frame de loading
            self.loading_frame.destroy()
            
            # Crear interfaz real
            self.crear_interfaz()
            
            self.logger.info("✓ Interfaz cargada correctamente con lazy loading")
        
        except Exception as e:
            self.logger.error(f"Error al finalizar lazy loading: {e}")
            messagebox.showerror("Error", f"Error al cargar la interfaz: {e}")
    
    
    
    # =====================================
    # INTERFAZ - CONSTRUCCIÓN
    # =====================================
    
    def crear_interfaz(self):
        """Crea todos los elementos de la interfaz."""
        # Frame principal con scroll
        self.main_frame = ctk.CTkScrollableFrame(
            self,
            fg_color=self.COLORES['bg_principal']
        )
        self.main_frame.pack(fill='both', expand=True, padx=20, pady=20)
        
        # Crear secciones
        self.crear_header()
        self.crear_selector_navegador()
        self.crear_seccion_excel()
        self.crear_botones_accion()
        self.crear_area_logs()
        self.crear_footer()
    
    
    def crear_header(self):
        """Crea el encabezado de la aplicación."""
        header_frame = ctk.CTkFrame(self.main_frame, fg_color="transparent")
        header_frame.pack(fill='x', pady=(0, 20))
        
        # Título con frame contenedor
        title_frame = ctk.CTkFrame(header_frame, fg_color="transparent")
        title_frame.pack(side='left', fill='x', expand=True)
        
        titulo = ctk.CTkLabel(
            title_frame,
            text="📱 WhatsApp Web - Envío Masivo",
            font=("Segoe UI", 28, "bold"),
            text_color=self.COLORES['turquesa']
        )
        titulo.pack(anchor='w')
        
        subtitulo = ctk.CTkLabel(
            title_frame,
            text="Versión 2.3 - Sprint 3.1 | Selenium Manager + Gestión de Perfiles",
            font=("Segoe UI", 12),
            text_color=self.COLORES['gris_medio']
        )
        subtitulo.pack(anchor='w', pady=(5, 0))
        
        # Frame para botones de tema (derecha)
        theme_frame = ctk.CTkFrame(header_frame, fg_color="transparent")
        theme_frame.pack(side='right', padx=(10, 0))
        
        # Título de temas
        theme_label = ctk.CTkLabel(
            theme_frame,
            text="Temas:",
            font=("Segoe UI", 11),
            text_color=self.COLORES['gris_medio']
        )
        theme_label.pack(pady=(0, 5))
        
        # Botones de tema
        buttons_container = ctk.CTkFrame(theme_frame, fg_color="transparent")
        buttons_container.pack()
        
        # Botón Modo Oscuro
        dark_btn = ThemeToggleButton(
            buttons_container,
            theme_manager=self.theme_manager,
            theme_name="dark",
            icon_text="🌙",
            command=lambda: self.cambiar_tema("dark")
        )
        dark_btn.pack(side='left', padx=2)
        self.theme_buttons['dark'] = dark_btn
        
        # Botón Modo Claro
        light_btn = ThemeToggleButton(
            buttons_container,
            theme_manager=self.theme_manager,
            theme_name="light",
            icon_text="☀️",
            command=lambda: self.cambiar_tema("light")
        )
        light_btn.pack(side='left', padx=2)
        self.theme_buttons['light'] = light_btn
    
    
    def crear_selector_navegador(self):
        """Crea el selector de navegador con botones de configuración."""
        frame = ctk.CTkFrame(self.main_frame, fg_color=self.COLORES['bg_secundario'], corner_radius=10)
        frame.pack(fill='x', pady=(0, 15))
        
        # Frame interno para padding
        inner_frame = ctk.CTkFrame(frame, fg_color="transparent")
        inner_frame.pack(fill='x', padx=20, pady=15)
        
        # Label
        label = ctk.CTkLabel(
            inner_frame,
            text="🌐 Navegador:",
            font=("Segoe UI", 14, "bold"),
            text_color=self.COLORES['gris_claro']
        )
        label.pack(side='left', padx=(0, 15))
        
        # ComboBox de navegadores
        self.combo_navegador = ctk.CTkComboBox(
            inner_frame,
            values=["Edge", "Chrome", "Firefox"],
            width=150,
            font=("Segoe UI", 12),
            dropdown_font=("Segoe UI", 11),
            fg_color=self.COLORES['bg_input'],
            button_color=self.COLORES['turquesa'],
            button_hover_color=self.COLORES['turquesa_hover'],
            border_color=self.COLORES['turquesa'],
            state="readonly"
        )
        self.combo_navegador.set("Edge")
        self.combo_navegador.pack(side='left', padx=(0, 10))
        
        # SPRINT 3.1: Botón "Configurar Perfil"
        self.btn_configurar_perfil = ctk.CTkButton(
            inner_frame,
            text="⚙️ Configurar Perfil",
            font=("Segoe UI", 12),
            fg_color=self.COLORES['turquesa'],
            hover_color=self.COLORES['turquesa_hover'],
            text_color="white",
            corner_radius=8,
            width=150,
            height=32,
            command=self.configurar_perfil_navegador
        )
        self.btn_configurar_perfil.pack(side='left', padx=(0, 10))
        
        # SPRINT 3.1: Botón "Probar Navegador"
        self.btn_probar_navegador = ctk.CTkButton(
            inner_frame,
            text="🌐 Probar Navegador",
            font=("Segoe UI", 12),
            fg_color=self.COLORES['verde'],
            hover_color="#1a8754",
            text_color="white",
            corner_radius=8,
            width=150,
            height=32,
            command=self.probar_navegador
        )
        self.btn_probar_navegador.pack(side='left')
    
    
    def crear_seccion_excel(self):
        """Crea la sección de carga de archivo Excel."""
        frame = ctk.CTkFrame(self.main_frame, fg_color=self.COLORES['bg_secundario'], corner_radius=10)
        frame.pack(fill='x', pady=(0, 15))
        
        # Frame interno
        inner_frame = ctk.CTkFrame(frame, fg_color="transparent")
        inner_frame.pack(fill='x', padx=20, pady=15)
        
        # Label
        label = ctk.CTkLabel(
            inner_frame,
            text="📂 Archivo Excel:",
            font=("Segoe UI", 14, "bold"),
            text_color=self.COLORES['gris_claro']
        )
        label.pack(anchor='w', pady=(0, 10))
        
        # Frame para input y botón
        input_frame = ctk.CTkFrame(inner_frame, fg_color="transparent")
        input_frame.pack(fill='x')
        
        # Entry
        self.entry_excel = ctk.CTkEntry(
            input_frame,
            placeholder_text="Selecciona un archivo Excel (.xlsx)",
            font=("Segoe UI", 12),
            height=40,
            fg_color=self.COLORES['bg_input'],
            border_color=self.COLORES['turquesa']
        )
        self.entry_excel.pack(side='left', fill='x', expand=True, padx=(0, 10))
        
        # Botón
        btn_examinar = ctk.CTkButton(
            input_frame,
            text="📁 Examinar",
            font=("Segoe UI", 12, "bold"),
            fg_color=self.COLORES['turquesa'],
            hover_color=self.COLORES['turquesa_hover'],
            text_color="white",
            corner_radius=8,
            width=120,
            height=40,
            command=self.seleccionar_excel
        )
        btn_examinar.pack(side='left')
    
    
    def crear_botones_accion(self):
        """Crea los botones principales de acción."""
        frame = ctk.CTkFrame(self.main_frame, fg_color="transparent")
        frame.pack(fill='x', pady=(0, 15))
        
        # Botón Iniciar
        self.btn_iniciar = ctk.CTkButton(
            frame,
            text="▶️ INICIAR ENVÍO MASIVO",
            font=("Segoe UI", 16, "bold"),
            fg_color=self.COLORES['verde'],
            hover_color="#1a8754",
            text_color="white",
            corner_radius=10,
            height=50,
            command=self.iniciar_proceso
        )
        self.btn_iniciar.pack(fill='x', pady=(0, 10))
        
        # Label informativo
        self.label_info = ctk.CTkLabel(
            frame,
            text="ℹ️ Carga un archivo Excel y selecciona un navegador para comenzar",
            font=("Segoe UI", 11),
            text_color=self.COLORES['gris_medio']
        )
        self.label_info.pack()
    
    
    def crear_area_logs(self):
        """Crea el área de logs."""
        frame = ctk.CTkFrame(self.main_frame, fg_color=self.COLORES['bg_secundario'], corner_radius=10)
        frame.pack(fill='both', expand=True, pady=(0, 15))
        
        # Frame interno
        inner_frame = ctk.CTkFrame(frame, fg_color="transparent")
        inner_frame.pack(fill='both', expand=True, padx=20, pady=15)
        
        # Label
        label = ctk.CTkLabel(
            inner_frame,
            text="📋 Registro de Actividad:",
            font=("Segoe UI", 14, "bold"),
            text_color=self.COLORES['gris_claro']
        )
        label.pack(anchor='w', pady=(0, 10))
        
        # TextBox
        self.text_logs = ctk.CTkTextbox(
            inner_frame,
            font=("Consolas", 10),
            fg_color=self.COLORES['bg_principal'],
            text_color=self.COLORES['gris_claro'],
            wrap="word",
            height=250
        )
        self.text_logs.pack(fill='both', expand=True)
    
    
    def crear_footer(self):
        """Crea el pie de página."""
        footer = ctk.CTkLabel(
            self.main_frame,
            text="© 2025 Blitz WaSenderBot. 🚀 Solución de mensajería masiva automatizada. Desarrollado por Ricardo Uculmana Quispe con Python + Selenium",
            font=("Segoe UI", 12),
            text_color=self.COLORES['gris_medio']
        )
        footer.pack(pady=(10, 0))
    
    
    
    # =====================================
    # SPRINT 3.1: MÉTODOS DE GESTIÓN DE PERFILES
    # =====================================
    
    def configurar_perfil_navegador(self):
        """
        SPRINT 3.1: Crea la carpeta de perfil del navegador seleccionado.
        """
        try:
            navegador = self.combo_navegador.get()
            ruta_perfil = obtener_ruta_perfiles(navegador)
            
            # Crear carpeta si no existe
            if not os.path.exists(ruta_perfil):
                os.makedirs(ruta_perfil)
                self.agregar_log(f"✓ Perfil creado: {ruta_perfil}")
                self.logger.info(f"Perfil creado para {navegador}: {ruta_perfil}")
                messagebox.showinfo(
                    "Perfil Creado",
                    f"Se ha creado el perfil para {navegador}\n\n"
                    f"Ruta: {ruta_perfil}\n\n"
                    f"Ahora puedes usar el botón 'Probar Navegador' para sincronizar WhatsApp."
                )
            else:
                self.agregar_log(f"ℹ️ El perfil ya existe: {ruta_perfil}")
                messagebox.showinfo(
                    "Perfil Existente",
                    f"El perfil para {navegador} ya existe\n\n"
                    f"Ruta: {ruta_perfil}"
                )
        
        except Exception as e:
            error_msg = f"Error al crear perfil: {str(e)}"
            self.agregar_log(f"✗ {error_msg}")
            self.logger.error(error_msg)
            messagebox.showerror("Error", error_msg)
    
    
    def probar_navegador(self):
        """
        SPRINT 3.1: Abre el navegador en WhatsApp Web para que el usuario sincronice manualmente.
        """
        try:
            navegador = self.combo_navegador.get()
            navegador_lower = navegador.lower()
            ruta_perfil = obtener_ruta_perfiles(navegador_lower)
            
            # Verificar que exista el perfil
            if not os.path.exists(ruta_perfil):
                messagebox.showwarning(
                    "Perfil No Encontrado",
                    f"Primero debes crear el perfil usando el botón 'Configurar Perfil'"
                )
                return
            
            self.agregar_log(f"🌐 Abriendo {navegador} para prueba...")
            self.logger.info(f"Abriendo {navegador} para configuración de WhatsApp")
            
            # Configurar opciones del navegador
            if navegador_lower == "edge":
                options = EdgeOptions()
                options.add_argument(f"user-data-dir={ruta_perfil}")
                options.add_argument("--start-maximized")
                options.add_argument("--disable-blink-features=AutomationControlled")
                options.add_experimental_option("excludeSwitches", ["enable-automation"])
                options.add_experimental_option('useAutomationExtension', False)
                
                driver = webdriver.Edge(options=options)
                
            elif navegador_lower == "chrome":
                options = ChromeOptions()
                options.add_argument(f"user-data-dir={ruta_perfil}")
                options.add_argument("--start-maximized")
                options.add_argument("--disable-blink-features=AutomationControlled")
                options.add_experimental_option("excludeSwitches", ["enable-automation"])
                options.add_experimental_option('useAutomationExtension', False)
                
                driver = webdriver.Chrome(options=options)
                
            else:  # Firefox
                options = FirefoxOptions()
                options.add_argument("-profile")
                options.add_argument(ruta_perfil)
                options.set_preference("dom.webdriver.enabled", False)
                options.set_preference('useAutomationExtension', False)
                
                driver = webdriver.Firefox(options=options)
                driver.maximize_window()
            
            driver.get("https://web.whatsapp.com")
            
            self.agregar_log(f"✓ {navegador} abierto en WhatsApp Web")
            self.agregar_log(f"ℹ️ Sincroniza tu cuenta y cierra el navegador cuando termines")
            
            messagebox.showinfo(
                "Navegador Abierto",
                f"{navegador} se ha abierto en WhatsApp Web\n\n"
                f"1. Escanea el código QR con tu teléfono\n"
                f"2. Espera a que cargue completamente\n"
                f"3. Cierra el navegador cuando termines\n\n"
                f"El perfil quedará guardado para futuros envíos."
            )
        
        except Exception as e:
            error_msg = f"Error al abrir navegador: {str(e)}"
            self.agregar_log(f"✗ {error_msg}")
            self.logger.error(error_msg)
            messagebox.showerror("Error", error_msg)
    
    
    
    # =====================================
    # MÉTODOS DE CAMBIO DE TEMA
    # =====================================
    
    def cambiar_tema(self, tema_id):
        """
        Cambia el tema de la aplicación.
        
        Args:
            tema_id (str): ID del tema ('dark', 'light', 'colorblind')
        """
        try:
            if self.theme_manager.set_theme(tema_id):
                self.configurar_colores()
                self.actualizar_colores_interfaz()
                
                # Actualizar estado de botones
                for theme_name, btn in self.theme_buttons.items():
                    btn.set_active(theme_name == tema_id)
                
                # Log del cambio
                theme_names = {
                    "dark": "Modo Oscuro 🌙",
                    "light": "Modo Claro ☀️"
                }
                self.agregar_log(f"✓ Tema cambiado a: {theme_names.get(tema_id, tema_id)}")
        
        except Exception as e:
            self.agregar_log(f"✗ Error al cambiar tema: {e}")
    
    
    def actualizar_colores_interfaz(self):
        """Actualiza los colores de todos los componentes de la interfaz."""
        try:
            # Ventana principal
            self.configure(fg_color=self.COLORES['bg_principal'])
            
            # Main frame
            if hasattr(self, 'main_frame'):
                self.main_frame.configure(fg_color=self.COLORES['bg_principal'])
            
            # Actualizar todos los frames secundarios
            for widget in self.main_frame.winfo_children():
                if isinstance(widget, ctk.CTkFrame):
                    # Frames con fondo secundario
                    if widget.cget("fg_color") != "transparent":
                        widget.configure(fg_color=self.COLORES['bg_secundario'])
            
            # Actualizar entries
            if hasattr(self, 'entry_excel'):
                self.entry_excel.configure(
                    fg_color=self.COLORES['bg_input'],
                    border_color=self.COLORES['turquesa'],
                    text_color=self.COLORES['gris_claro']
                )
            
            # Actualizar combo navegador
            if hasattr(self, 'combo_navegador'):
                self.combo_navegador.configure(
                    fg_color=self.COLORES['bg_input'],
                    button_color=self.COLORES['turquesa'],
                    button_hover_color=self.COLORES['turquesa_hover'],
                    border_color=self.COLORES['turquesa'],
                    text_color=self.COLORES['gris_claro']
                )
            
            # SPRINT 3.1: Actualizar botones de perfil
            if hasattr(self, 'btn_configurar_perfil'):
                self.btn_configurar_perfil.configure(
                    fg_color=self.COLORES['turquesa'],
                    hover_color=self.COLORES['turquesa_hover'],
                    text_color="white"
                )
            
            if hasattr(self, 'btn_probar_navegador'):
                self.btn_probar_navegador.configure(
                    fg_color=self.COLORES['verde'],
                    hover_color="#1a8754",
                    text_color="white"
                )
            
            # Actualizar botón iniciar
            if hasattr(self, 'btn_iniciar'):
                self.btn_iniciar.configure(
                    fg_color=self.COLORES['verde'],
                    hover_color="#1a8754",
                    text_color="white"
                )
            
            # Actualizar área de logs
            if hasattr(self, 'text_logs'):
                self.text_logs.configure(
                    fg_color=self.COLORES['bg_principal'],
                    text_color=self.COLORES['gris_claro']
                )
            
            # Actualizar labels principales
            if hasattr(self, 'label_info'):
                self.label_info.configure(text_color=self.COLORES['gris_medio'])
            
            # Actualizar todos los labels en main_frame
            for widget in self.main_frame.winfo_children():
                self._actualizar_labels_recursivo(widget)
        
        except Exception as e:
            print(f"Error al actualizar colores: {e}")
    
    
    def _actualizar_labels_recursivo(self, widget):
        """
        Actualiza recursivamente los colores de texto de todos los labels.
        
        Args:
            widget: Widget a procesar
        """
        try:
            # Si es un label, actualizar su color de texto
            if isinstance(widget, ctk.CTkLabel):
                # Verificar si el label tiene un color específico asignado
                current_color = widget.cget("text_color")
                
                # Solo actualizar si es un color del sistema (no personalizado como turquesa del título)
                if current_color in ["white", "#FFFFFF", "#CCCCCC", "#666666", "gray", "black", "#000000"]:
                    widget.configure(text_color=self.COLORES['gris_claro'])
            
            # Si es un contenedor, procesar sus hijos
            if hasattr(widget, 'winfo_children'):
                for child in widget.winfo_children():
                    self._actualizar_labels_recursivo(child)
        
        except Exception as e:
            pass  # Ignorar errores en widgets individuales
    
    
    
    # =====================================
    # MÉTODOS DE FUNCIONALIDAD
    # =====================================
    
    def agregar_log(self, mensaje):
        """Agrega un mensaje al área de logs."""
        timestamp = datetime.now().strftime("%H:%M:%S")
        self.text_logs.insert("end", f"[{timestamp}] {mensaje}\n")
        self.text_logs.see("end")
    
    
    def seleccionar_excel(self):
        """Abre diálogo para seleccionar archivo Excel."""
        archivo = filedialog.askopenfilename(
            title="Seleccionar archivo Excel",
            filetypes=[("Excel files", "*.xlsx"), ("All files", "*.*")]
        )
        
        if archivo:
            self.ruta_excel = archivo
            self.entry_excel.delete(0, 'end')
            self.entry_excel.insert(0, archivo)
            self.agregar_log(f"✓ Archivo seleccionado: {Path(archivo).name}")
            self.logger.info(f"Archivo Excel seleccionado: {archivo}")
    
    
    def inicializar_driver(self):
        """
        Inicializa el WebDriver según el navegador seleccionado.
        Selenium Manager gestiona automáticamente los drivers.
        
        Returns:
            WebDriver: Instancia del driver o None si hay error
        """
        try:
            navegador = self.navegador_seleccionado.lower()
            ruta_perfil = obtener_ruta_perfiles(navegador)
            
            self.agregar_log(f"Inicializando {self.navegador_seleccionado}...")
            self.agregar_log(f"Perfil: {ruta_perfil}")
            self.agregar_log("Selenium Manager gestionando driver automáticamente...")
            self.logger.info(f"Inicializando driver de {self.navegador_seleccionado}")
            self.logger.info(f"Perfil: {ruta_perfil}")
            self.logger.info("Selenium Manager auto-gestionando driver")
            
            if navegador == "edge":
                options = EdgeOptions()
                options.add_argument(f"user-data-dir={ruta_perfil}")
                options.add_argument("--start-maximized")
                options.add_argument("--disable-blink-features=AutomationControlled")
                options.add_experimental_option("excludeSwitches", ["enable-automation"])
                options.add_experimental_option('useAutomationExtension', False)
                
                driver = webdriver.Edge(options=options)
                
            elif navegador == "chrome":
                options = ChromeOptions()
                options.add_argument(f"user-data-dir={ruta_perfil}")
                options.add_argument("--start-maximized")
                options.add_argument("--disable-blink-features=AutomationControlled")
                options.add_experimental_option("excludeSwitches", ["enable-automation"])
                options.add_experimental_option('useAutomationExtension', False)
                
                driver = webdriver.Chrome(options=options)
                
            elif navegador == "firefox":
                options = FirefoxOptions()
                options.add_argument("-profile")
                options.add_argument(ruta_perfil)
                options.set_preference("dom.webdriver.enabled", False)
                options.set_preference('useAutomationExtension', False)
                
                driver = webdriver.Firefox(options=options)
                driver.maximize_window()
            
            else:
                raise ValueError(f"Navegador no soportado: {self.navegador_seleccionado}")
            
            self.agregar_log(f"✓ {self.navegador_seleccionado} inicializado correctamente")
            self.logger.info(f"✓ Driver de {self.navegador_seleccionado} inicializado")
            return driver
            
        except Exception as e:
            self.agregar_log(f"✗ Error al inicializar driver: {str(e)}")
            self.logger.error(f"Error al inicializar driver: {str(e)}")
            return None
    
    
    def iniciar_proceso(self):
        """Inicia el proceso de envío masivo."""
        # Validar que se haya seleccionado un archivo
        if not self.ruta_excel:
            messagebox.showwarning("Advertencia", "Debes seleccionar un archivo Excel primero")
            return
        
        # Validar que el archivo exista
        if not os.path.exists(self.ruta_excel):
            messagebox.showerror("Error", "El archivo seleccionado no existe")
            return
        
        # Obtener navegador seleccionado
        self.navegador_seleccionado = self.combo_navegador.get()
        
        # Confirmar inicio
        respuesta = messagebox.askyesno(
            "Confirmar Envío",
            f"¿Deseas iniciar el envío masivo?\n\n"
            f"Archivo: {Path(self.ruta_excel).name}\n"
            f"Navegador: {self.navegador_seleccionado}\n\n"
            f"Este proceso puede tardar varios minutos."
        )
        
        if respuesta:
            self.agregar_log("="*50)
            self.agregar_log("🚀 Iniciando proceso de envío masivo...")
            self.agregar_log(f"📂 Archivo: {Path(self.ruta_excel).name}")
            self.agregar_log(f"🌐 Navegador: {self.navegador_seleccionado}")
            self.agregar_log("="*50)
            
            # Deshabilitar botón
            self.btn_iniciar.configure(state="disabled")
            self.label_info.configure(
                text="⏳ Procesando envío... Por favor espera",
                text_color=self.COLORES['amarillo']
            )
            
            # Ejecutar en thread separado
            threading.Thread(target=self.ejecutar_envio, daemon=True).start()
    
    
    def verificar_bateria(self):
        """
        SPRINT 3: Verifica el estado de la batería del sistema.
        
        Returns:
            tuple: (bool, str) - (puede_continuar, mensaje)
        """
        try:
            battery = psutil.sensors_battery()
            
            if battery is None:
                # No hay batería (PC de escritorio)
                return True, "Sistema conectado a corriente (sin batería)"
            
            porcentaje = battery.percent
            conectado = battery.power_plugged
            
            if conectado:
                return True, f"Batería al {porcentaje}% y conectada a corriente"
            else:
                if porcentaje < 20:
                    return False, f"Batería baja ({porcentaje}%). Conecta el cargador antes de continuar"
                elif porcentaje < 50:
                    return True, f"Batería al {porcentaje}%. Se recomienda conectar cargador para envíos largos"
                else:
                    return True, f"Batería al {porcentaje}%"
        
        except Exception as e:
            self.logger.warning(f"No se pudo verificar batería: {e}")
            return True, "No se pudo verificar el estado de la batería"
    
    
    def ejecutar_envio(self):
        """Ejecuta el proceso completo de envío masivo."""
        try:
            # SPRINT 3: Registrar tiempo de inicio
            tiempo_inicio = time.time()
            
            # SPRINT 3: Verificar batería antes de iniciar
            puede_continuar, mensaje_bateria = self.verificar_bateria()
            self.agregar_log(f"🔋 {mensaje_bateria}")
            self.logger.info(f"Estado de batería: {mensaje_bateria}")
            
            if not puede_continuar:
                self.agregar_log("⚠️ Proceso detenido: Batería insuficiente")
                messagebox.showwarning("Batería Baja", mensaje_bateria)
                self.btn_iniciar.configure(state="normal")
                self.label_info.configure(
                    text="⚠️ Proceso detenido: Conecta el cargador e intenta nuevamente",
                    text_color=self.COLORES['amarillo']
                )
                return
            
            # SPRINT 3: Activar prevención de suspensión
            self.prevenir_suspension()
            self.agregar_log("✓ Prevención de suspensión activada")
            
            self.enviando = True
            self.cancelar_envio = False
            
            # Logging inicial
            log_seccion(self.logger, f"INICIO DE ENVÍO MASIVO - {self.navegador_seleccionado}")
            self.logger.info(f"Navegador: {self.navegador_seleccionado}")
            self.logger.info(f"Archivo Excel: {self.ruta_excel}")
            self.logger.info("Driver: Selenium Manager (auto-gestionado)")
            
            # 1. Leer datos del Excel
            self.agregar_log("\n📖 Leyendo datos del Excel...")
            log_seccion(self.logger, "LECTURA DE DATOS")
            
            self.mensajes_dict = leer_mensajes(self.ruta_excel, self.logger)
            self.contactos_list = leer_contactos(self.ruta_excel, self.logger)
            
            self.logger.info(f"Mensajes encontrados: {len(self.mensajes_dict)}")
            self.logger.info(f"Contactos encontrados: {len(self.contactos_list)}")
            
            self.agregar_log(f"✓ {len(self.mensajes_dict)} mensajes encontrados")
            self.agregar_log(f"✓ {len(self.contactos_list)} contactos encontrados")
            
            # 2. Procesar datos
            self.agregar_log("\n⚙️ Procesando datos...")
            log_seccion(self.logger, "PROCESAMIENTO DE DATOS")
            
            self.datos_procesados, errores = procesar_datos(self.contactos_list, self.mensajes_dict, self.logger)
            
            if errores:
                self.agregar_log(f"⚠️ {len(errores)} errores de procesamiento")
            
            total_contactos = len(self.datos_procesados)
            self.agregar_log(f"✓ {total_contactos} envíos preparados")
            self.logger.info(f"Total de envíos a procesar: {total_contactos}")
            
            if total_contactos == 0:
                self.agregar_log("⚠️ No hay datos para procesar")
                messagebox.showwarning("Sin Datos", "No se encontraron datos válidos para enviar")
                return
            
            # 4. Inicializar navegador
            self.agregar_log("\n🌐 Iniciando navegador...")
            log_seccion(self.logger, "INICIALIZACIÓN DE NAVEGADOR")
            
            driver = self.inicializar_driver()
            
            if not driver:
                self.agregar_log("✗ No se pudo inicializar el driver")
                messagebox.showerror("Error", "No se pudo inicializar el navegador")
                return
            
            # 5. Abrir WhatsApp Web
            self.agregar_log("\n📱 Abriendo WhatsApp Web...")
            driver.get("https://web.whatsapp.com")
            
            # 6. Iniciar envío masivo
            self.agregar_log("\n📤 Iniciando envío masivo...")
            log_seccion(self.logger, "ENVÍO MASIVO DE MENSAJES")
            
            sender = WhatsAppSender(driver, self.logger)
            
            # Esperar carga de WhatsApp Web
            if not sender.esperar_carga_whatsapp(timeout=60):
                self.agregar_log("✗ WhatsApp Web no cargó correctamente")
                messagebox.showerror("Error", "WhatsApp Web no cargó. ¿Escaneaste el código QR?")
                driver.quit()
                return
            
            self.agregar_log("✓ WhatsApp Web cargado correctamente")
            
            log_seccion(self.logger, "INICIANDO ENVÍOS")
            
            # SPRINT 3: Prevención de suspensión ya está activada desde antes
            
            # Variables de control
            enviados = 0
            fallidos = 0
            resultados = []
            
            # Procesar cada contacto
            for idx, datos in enumerate(self.datos_procesados, 1):
                try:
                    self.agregar_log(f"\n[{idx}/{total_contactos}] Enviando a {datos['destinatario']}...")
                    
                    # Enviar mensaje
                    exito, mensaje_resultado = sender.enviar_mensaje(
                        datos['codigo_pais'],
                        datos['numero'],
                        datos['mensaje']
                    )
                    
                    # Registrar resultado
                    if exito:
                        enviados += 1
                        estado = "EXITOSO"
                        self.agregar_log(f"✓ Enviado exitosamente")
                    else:
                        fallidos += 1
                        estado = "FALLIDO"
                        self.agregar_log(f"✗ Falló: {mensaje_resultado}")
                    
                    resultados.append({
                        'fila_excel': datos['fila_excel'],
                        'destinatario': datos['destinatario'],
                        'numero_completo': datos['numero_completo'],
                        'estado': estado,
                        'mensaje_resultado': mensaje_resultado,
                        'timestamp': datetime.now().strftime('%Y-%m-%d %H:%M:%S')
                    })
                    
                    # Delay aleatorio (excepto en el último)
                    if idx < total_contactos:
                        sender.aplicar_delay_aleatorio()
                
                except Exception as e:
                    fallidos += 1
                    self.logger.error(f"Error inesperado con {datos['destinatario']}: {str(e)}")
                    self.agregar_log(f"✗ Error inesperado: {str(e)}")

                    # Registrar el error en resultados
                    resultados.append({
                        'fila_excel': datos.get('fila_excel', 'N/A'),
                        'destinatario': datos.get('destinatario', 'Desconocido'),
                        'numero_completo': datos.get('numero_completo', 'N/A'),
                        'estado': 'FALLIDO',
                        'mensaje_resultado': f"Excepción: {str(e)}",
                        'timestamp': datetime.now().strftime('%Y-%m-%d %H:%M:%S')
                    })
            
            # 7. Generar reporte
            self.agregar_log("\n📊 Generando reporte...")
            log_seccion(self.logger, "GENERACIÓN DE REPORTE")
            
            # Reporte completo (único reporte con todos los envíos)
            ruta_reporte = generar_reporte(resultados, carpeta=self.LOGS_DIR, nombre_base="envios_whatsapp")
            self.agregar_log(f"✓ Reporte generado: {Path(ruta_reporte).name}")
            
            # Resumen final
            log_seccion(self.logger, "RESUMEN FINAL")
            self.logger.info(f"Total procesados: {total_contactos}")
            self.logger.info(f"Enviados exitosamente: {enviados}")
            self.logger.info(f"Fallidos: {fallidos}")
            
            tasa_exito = (enviados / total_contactos * 100) if total_contactos > 0 else 0
            self.logger.info(f"Tasa de éxito: {tasa_exito:.1f}%")
            
            self.agregar_log(f"\n{'='*50}")
            self.agregar_log(f"RESUMEN FINAL:")
            self.agregar_log(f"  Total: {total_contactos}")
            self.agregar_log(f"  Exitosos: {enviados}")
            self.agregar_log(f"  Fallidos: {fallidos}")
            self.agregar_log(f"  Tasa de éxito: {tasa_exito:.1f}%")
            self.agregar_log(f"{'='*50}")
            
            # Cerrar logger
            cerrar_logger(self.logger, "Proceso de envío finalizado")
            
            # SPRINT 3: Desactivar prevención de suspensión
            self.permitir_suspension()
            self.agregar_log("✓ Sistema puede suspenderse nuevamente")
            
            # SPRINT 3: Calcular tiempo total de ejecución
            tiempo_fin = time.time()
            duracion_total_segundos = int(tiempo_fin - tiempo_inicio)
            
            # Formatear duración en formato legible
            horas = duracion_total_segundos // 3600
            minutos = (duracion_total_segundos % 3600) // 60
            segundos = duracion_total_segundos % 60
            
            if horas > 0:
                duracion_formateada = f"{horas} hora{'s' if horas != 1 else ''} {minutos} minuto{'s' if minutos != 1 else ''} {segundos} segundo{'s' if segundos != 1 else ''}"
            elif minutos > 0:
                duracion_formateada = f"{minutos} minuto{'s' if minutos != 1 else ''} {segundos} segundo{'s' if segundos != 1 else ''}"
            else:
                duracion_formateada = f"{segundos} segundo{'s' if segundos != 1 else ''}"
            
            self.logger.info(f"⏱️ Tiempo total de ejecución: {duracion_formateada}")
            self.agregar_log(f"⏱️ Tiempo total de ejecución: {duracion_formateada}")
            
            # Cerrar driver
            driver.quit()
            self.agregar_log("✓ Navegador cerrado")
            
            # SPRINT 3: Notificar finalización con sonido, parpadeo y traer ventana al frente
            self.notificar_finalizacion()
            
            # Mensaje final
            messagebox.showinfo(
                "Proceso Completado",
                f"Envío masivo finalizado\n\n"
                f"Total: {total_contactos}\n"
                f"Exitosos: {enviados}\n"
                f"Fallidos: {fallidos}\n\n"
                f"⏱️ Tiempo de ejecución: {duracion_formateada}\n\n"
                f"Revisa los reportes en la carpeta 'logs'"
            )
            
        except Exception as e:
            self.agregar_log(f"✗ Error crítico: {str(e)}")
            if self.logger:
                self.logger.error(f"Error crítico: {str(e)}")
            messagebox.showerror("Error Crítico", f"Ocurrió un error crítico:\n{str(e)}")
        
        finally:
            # SPRINT 3: Asegurar desactivación de prevención de suspensión
            try:
                self.permitir_suspension()
            except:
                pass
            
            self.enviando = False
            self.btn_iniciar.configure(state="normal")
            self.label_info.configure(
                text="ℹ️ Proceso finalizado. Puedes iniciar un nuevo envío.",
                text_color=self.COLORES['gris_medio']
            )
    
    
    def prevenir_suspension(self):
        """
        SPRINT 3: Previene que el sistema operativo entre en suspensión durante el envío.
        Solo funciona en Windows.
        """
        try:
            import ctypes
            # ES_CONTINUOUS | ES_SYSTEM_REQUIRED | ES_DISPLAY_REQUIRED
            ctypes.windll.kernel32.SetThreadExecutionState(0x80000000 | 0x00000001 | 0x00000002)
            self.logger.info("✓ Prevención de suspensión activada")
        except Exception as e:
            self.logger.warning(f"No se pudo activar prevención de suspensión: {e}")
    
    
    def permitir_suspension(self):
        """
        SPRINT 3: Permite que el sistema operativo vuelva a entrar en suspensión.
        Solo funciona en Windows.
        """
        try:
            import ctypes
            # ES_CONTINUOUS (restaurar comportamiento normal)
            ctypes.windll.kernel32.SetThreadExecutionState(0x80000000)
            self.logger.info("✓ Sistema puede suspenderse nuevamente")
        except Exception as e:
            self.logger.warning(f"No se pudo desactivar prevención de suspensión: {e}")
    
    
    def notificar_finalizacion(self):
        """
        SPRINT 3: Notifica al usuario que el proceso finalizó con múltiples métodos:
        - Sonido del sistema
        - Parpadeo en barra de tareas
        - Traer ventana al frente
        - Dar foco a la ventana
        
        Este método debe ejecutarse en el thread principal de tkinter.
        """
        def ejecutar_notificacion():
            try:
                # 1. Emitir sonido del sistema (Windows)
                try:
                    import winsound
                    # Sonido de información del sistema (asterisco)
                    winsound.MessageBeep(winsound.MB_ICONASTERISK)
                except Exception as e:
                    self.logger.warning(f"No se pudo reproducir sonido: {e}")
                
                # 2. Des-minimizar si está minimizada
                try:
                    self.deiconify()
                except Exception as e:
                    self.logger.warning(f"No se pudo des-minimizar: {e}")
                
                # 3. Traer ventana al frente (funciona incluso si está tapada por otras ventanas)
                try:
                    self.lift()
                    self.attributes('-topmost', True)
                    self.after(100, lambda: self.attributes('-topmost', False))
                except Exception as e:
                    self.logger.warning(f"No se pudo traer ventana al frente: {e}")
                
                # 4. Dar foco a la ventana
                try:
                    self.focus_force()
                except Exception as e:
                    self.logger.warning(f"No se pudo dar foco: {e}")
                
                # 5. Parpadeo en barra de tareas (Windows)
                try:
                    import ctypes
                    hwnd = ctypes.windll.user32.GetParent(self.winfo_id())
                    
                    # FLASHWINFO structure
                    class FLASHWINFO(ctypes.Structure):
                        _fields_ = [
                            ('cbSize', ctypes.c_uint),
                            ('hwnd', ctypes.c_void_p),
                            ('dwFlags', ctypes.c_uint),
                            ('uCount', ctypes.c_uint),
                            ('dwTimeout', ctypes.c_uint)
                        ]
                    
                    # Configurar parpadeo
                    flash_info = FLASHWINFO()
                    flash_info.cbSize = ctypes.sizeof(FLASHWINFO)
                    flash_info.hwnd = hwnd
                    flash_info.dwFlags = 0x0000000F  # FLASHW_ALL (parpadea caption y taskbar)
                    flash_info.uCount = 3  # Número de parpadeos
                    flash_info.dwTimeout = 0  # Velocidad por defecto
                    
                    # Ejecutar parpadeo
                    ctypes.windll.user32.FlashWindowEx(ctypes.byref(flash_info))
                except Exception as e:
                    self.logger.warning(f"No se pudo hacer parpadeo en taskbar: {e}")
                
                self.logger.info("✓ Notificación de finalización ejecutada")
            
            except Exception as e:
                self.logger.error(f"Error en notificación de finalización: {e}")
        
        # Ejecutar en el thread principal de tkinter
        self.after(0, ejecutar_notificacion)


# ==================== PUNTO DE ENTRADA ====================
if __name__ == "__main__":
    app = WhatsAppGUI()
    app.mainloop()