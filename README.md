# 🤖 BLITZ-WASENDER: Bot de WhatsApp para Envío Masivo

![CustomTkinter GUI Screenshot] 
Un bot de escritorio desarrollado en Python, diseñado para automatizar el envío de mensajes masivos y personalizados a través de **WhatsApp Web**. Utiliza **CustomTkinter** para una interfaz de usuario limpia y **Excel (.xlsx)** como fuente de datos para los contactos y mensajes.

## 🌟 Características Principales

* **Interfaz Gráfica (GUI):** Desarrollado con CustomTkinter para una experiencia moderna y fácil de usar.
* **Gestión de Contactos:** Carga la lista de destinatarios directamente desde el archivo `contactos.xlsx`.
* **Automatización Segura:** Utiliza **Selenium** y **webdriver-manager** para controlar WhatsApp Web de forma robusta.
* **Persistencia de Sesión:** Manejo de perfiles de navegador para evitar iniciar sesión repetidamente.
* **Logging Detallado:** Generación de archivos de registro (`logs/`) para seguimiento de errores y estado de los envíos.

## ⚙️ Requisitos del Sistema

* **Python 3.8+**
* **Navegador Web Compatible:** Google Chrome, Edge o Firefox (dependiendo de la configuración de `webdriver-manager`).

## 🚀 Instalación y Uso

Sigue estos pasos para poner en marcha el bot.

### 1. Clonar el Repositorio

Abre tu terminal y clona el proyecto:

```bash
git clone <URL_DE_TU_REPOSITORIO>
cd BLITZ-WASENDER
```

### 2. Crear y activar entorno virtual
python -m venv .venv
# Para Windows:
.venv\Scripts\activate
# Para Linux/Mac:
source .venv/bin/activate

### 3. Instalar Dependencias

pip install -r requirements.txt

### 4. Configuración del Bot

1. Plantilla de contactos: Abre el archivo contactos.xlsx y rellena los datos de tus destinatarios. Asegúrate de que las columnas coincidan con el formato esperado por el bot (e.g., Columna para el Número, Columna para el Mensaje, etc.).
2. Archivos de Recursos: Los archivos de configuración visual (recursos/themes.json) y el ícono (recursos/app_icon.ico) son esenciales y deben permanecer en la carpeta recursos/.

### 5. Ejecutar la aplicación

Con el entorno virtual activado, inicia la interfaz gráfica:
python gui_app.py


📁 Estructura del Proyecto

BLITZ-WASENDER/
├── .gitignore          # Archivo crucial para ignorar carpetas y archivos temporales (.venv, logs/, etc.).
├── README.md           # Documentación principal del proyecto (la carta de presentación).
├── requirements.txt    # Lista de dependencias de Python para la instalación.
├── contactos.xlsx      # Plantilla de Excel para la base de datos de envío.
├── gui_app.py          # Script principal que ejecuta y coordina la Interfaz Gráfica (CustomTkinter).
├── onedir.py           # Script o utilitario relacionado con el empaquetado/distribución (e.g., PyInstaller).
│
├── recursos/           # Carpeta que contiene archivos estáticos necesarios para la GUI.
│   ├── app_icon.ico    # Ícono de la aplicación.
│   └── themes.json     # Archivo de configuración visual de CustomTkinter.
│
└── utils/              # PAQUETE DE UTILIDADES y LÓGICA DE NEGOCIO
    ├── __init__.py     # Inicializa el paquete. Contiene módulos para logging, validación, Excel y envío de mensajes.
    │
    ├── excel_handler.py    # Módulo para manejo de archivos Excel.
    │                       # Lógica de lectura, validación, y generación de reportes (con telemetría y naming dinámico).
    │
    ├── logger.py           # Módulo para gestión de logs.
    │                       # Crea logs únicos por ejecución con timestamp y soporta rutas dinámicas (desarrollo vs. distribución).
    │
    ├── theme_manager.py    # Lógica para el cambio entre tema claro y oscuro de la aplicación.
    ├── ui_components.py    # Define Widgets personalizados de CustomTkinter que se adaptan al tema.
    ├── ui_layout.py        # Funciones que construyen y retornan secciones completas de la interfaz.
    ├── validators.py       # Funciones para la validación de archivos, rutas, números y estructura de Excel.
    └── whatsapp_sender.py  # Módulo para envío de mensajes por WhatsApp Web. Maneja la lógica de automatización