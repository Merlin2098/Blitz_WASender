# 🤖 BLITZ-WASENDER: Bot de WhatsApp para Envío Masivo

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
├── .gitignore              # Define qué archivos y carpetas deben excluirse del control de versiones (ej. .venv, /logs, etc.)
├── README.md               # Documentación principal del proyecto (esta guía).
├── requirements.txt        # Lista de dependencias de Python requeridas para ejecutar la aplicación.
├── contactos.xlsx          # Plantilla de ejemplo para la base de datos de contactos (archivo Excel).
├── gui_app.py              # Script principal que ejecuta y coordina la Interfaz Gráfica (basada en CustomTkinter).
├── onedir.py               # Script auxiliar para empaquetado/distribución (por ejemplo, con PyInstaller).
│
├── recursos/               # Carpeta con archivos estáticos y de configuración visual.
│   ├── app_icon.ico        # Ícono principal de la aplicación.
│   └── themes.json         # Configuración de temas (modo claro/oscuro) para CustomTkinter.
│
└── utils/                  # Paquete con módulos de lógica interna y utilidades.
    ├── __init__.py             # Inicializa el paquete y permite la importación modular.
    │
    ├── excel_handler.py        # Maneja operaciones con archivos Excel:
    │                           #   - Lectura y validación de datos
    │                           #   - Generación de reportes y telemetría
    │                           #   - Creación de nombres de archivo dinámicos
    │
    ├── logger.py               # Gestión centralizada de logs:
    │                           #   - Crea registros únicos por ejecución
    │                           #   - Incluye timestamp y soporte de rutas dinámicas
    │
    ├── theme_manager.py        # Controla la lógica del cambio de tema (claro ↔ oscuro).
    ├── ui_components.py        # Define widgets personalizados que se adaptan al tema actual.
    ├── ui_layout.py            # Construye y organiza las secciones principales de la interfaz gráfica.
    ├── validators.py           # Funciones para validar rutas, números y estructura de archivos Excel.
    └── whatsapp_sender.py      # Módulo de automatización de WhatsApp Web:
                                #   - Control de navegador
                                #   - Envío de mensajes
                                #   - Manejo de errores y sincronización
