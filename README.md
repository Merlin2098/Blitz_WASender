# 🤖 BLITZ-WASENDER: Bot de WhatsApp para Envío Masivo

Un bot de escritorio desarrollado en Python, diseñado para automatizar el envío de mensajes masivos y personalizados a través de **WhatsApp Web**. Utiliza **CustomTkinter** para una interfaz de usuario limpia y moderna, y **Excel (.xlsx)** como fuente de datos para los contactos y mensajes.

## 📋 Tabla de Contenidos

- [Características Principales](#-características-principales)
- [Requisitos del Sistema](#️-requisitos-del-sistema)
- [Instalación y Uso](#-instalación-y-uso)
  - [1. Clonar el Repositorio](#1-clonar-el-repositorio)
  - [2. Crear y Activar Entorno Virtual](#2-crear-y-activar-entorno-virtual)
  - [3. Instalar Dependencias](#3-instalar-dependencias)
  - [4. Configuración del Bot](#4-configuración-del-bot)
  - [5. Ejecutar la Aplicación](#5-ejecutar-la-aplicación)
  - [6. Crear Ejecutable (Opcional)](#6-crear-ejecutable-opcional)
- [Estructura del Proyecto](#-estructura-del-proyecto)
- [Formato del Archivo de Contactos](#-formato-del-archivo-de-contactos)
- [Solución de Problemas](#-solución-de-problemas)
- [Logs y Reportes](#-logs-y-reportes)
- [Advertencias Importantes](#️-advertencias-importantes)
- [Contribuciones](#-contribuciones)
- [Licencia](#-licencia)
- [Soporte](#-soporte)

## 🌟 Características Principales

* **Interfaz Gráfica Moderna:** Desarrollado con CustomTkinter para una experiencia de usuario intuitiva y atractiva.
* **Gestión de Contactos:** Carga la lista de destinatarios directamente desde el archivo `contactos.xlsx`.
* **Automatización Robusta:** Utiliza **Selenium** y **webdriver-manager** para controlar WhatsApp Web de forma segura y confiable.
* **Persistencia de Sesión:** Manejo automático de perfiles de navegador para evitar iniciar sesión repetidamente.
* **Logging Detallado:** Generación automática de archivos de registro (`logs/`) para seguimiento de errores y estado de los envíos.
* **Soporte de Temas:** Interfaz adaptable con modo claro y oscuro.
* **Validación de Datos:** Sistema integrado de validación para números telefónicos y estructura de archivos.

## ⚙️ Requisitos del Sistema

* **Python 3.8+**
* **Navegador Web Compatible:** Google Chrome, Edge o Firefox (se recomienda Chrome)
* **Sistema Operativo:** Windows, Linux o macOS

## 🚀 Instalación y Uso

Sigue estos pasos para poner en marcha el bot.

### 1. Clonar el Repositorio

Abre tu terminal y clona el proyecto:

```bash
git clone <URL_DE_TU_REPOSITORIO>
cd BLITZ-WASENDER
```

### 2. Crear y Activar Entorno Virtual

```bash
python -m venv .venv

# Para Windows:
.venv\Scripts\activate

# Para Linux/Mac:
source .venv/bin/activate
```

### 3. Instalar Dependencias

```bash
pip install -r requirements.txt
```

### 4. Configuración del Bot

1. **Plantilla de contactos:** Abre el archivo `contactos.xlsx` y rellena los datos de tus destinatarios. Asegúrate de que las columnas coincidan con el formato esperado por el bot (Número de teléfono, Mensaje, etc.).

2. **Archivos de Recursos:** Los archivos de configuración visual (`recursos/themes.json`) y el ícono (`recursos/app_icon.ico`) son esenciales y deben permanecer en la carpeta `recursos/`.

### 5. Ejecutar la Aplicación

Con el entorno virtual activado, inicia la interfaz gráfica:

```bash
python gui_app.py
```

### 6. Crear Ejecutable (Opcional)

Para distribuir la aplicación sin necesidad de Python:

```bash
python onedir.py
```

Este script genera un ejecutable empaquetado con PyInstaller.

## 📁 Estructura del Proyecto

```
BLITZ-WASENDER/
├── .gitignore              # Define archivos y carpetas excluidos del control de versiones
├── README.md               # Documentación principal del proyecto
├── requirements.txt        # Dependencias de Python requeridas
├── contactos.xlsx          # Plantilla de ejemplo para la base de datos de contactos
├── gui_app.py              # Script principal - Punto de entrada de la aplicación
├── onedir.py               # Script para crear ejecutable con PyInstaller
│
├── recursos/               # Recursos estáticos y configuración visual
│   ├── app_icon.ico        # Ícono de la aplicación
│   └── themes.json         # Configuración de temas (claro/oscuro)
│
└── utils/                  # Módulos de lógica interna y utilidades
    ├── __init__.py         # Inicializa el paquete utils
    ├── excel_handler.py    # Gestión de archivos Excel:
    │                       #   - Lectura y validación de datos
    │                       #   - Generación de reportes y telemetría
    │                       #   - Creación de nombres de archivo dinámicos
    ├── logger.py           # Sistema de logging:
    │                       #   - Registros únicos por ejecución
    │                       #   - Timestamp y rutas dinámicas
    ├── theme_manager.py    # Gestión de temas (claro ↔ oscuro)
    ├── ui_components.py    # Widgets personalizados adaptables al tema
    ├── ui_layout.py        # Construcción y organización de la interfaz
    ├── validators.py       # Validación de rutas, números y estructura Excel
    └── whatsapp_sender.py  # Automatización de WhatsApp Web:
                            #   - Control del navegador (Selenium)
                            #   - Envío de mensajes
                            #   - Manejo de errores y sincronización
```

## 📝 Formato del Archivo de Contactos

El archivo `contactos.xlsx` debe contener las siguientes columnas:

| Columna | Descripción | Ejemplo |
|---------|-------------|---------|
| Número | Número telefónico con código de país | +51987654321 |
| Mensaje | Texto del mensaje a enviar | Hola {nombre}, te saluda... |
| Nombre | Nombre del contacto (opcional para personalización) | Juan Pérez |

## 🔧 Solución de Problemas

### El navegador no abre WhatsApp Web
- Asegúrate de tener instalado Chrome o el navegador configurado
- Verifica tu conexión a internet
- Revisa los logs en la carpeta `logs/`

### Los mensajes no se envían
- Confirma que has escaneado el código QR en WhatsApp Web
- Verifica el formato de los números telefónicos en `contactos.xlsx`
- Asegúrate de que los contactos existan en WhatsApp

### Error al leer el archivo Excel
- Verifica que `contactos.xlsx` esté cerrado al ejecutar el bot
- Confirma que las columnas tengan los nombres correctos
- Revisa que no haya celdas vacías en las columnas obligatorias

## 📊 Logs y Reportes

La aplicación genera automáticamente:
- **Archivos de log** en `logs/`: Registro detallado de cada ejecución
- **Reportes de envío**: Estado de cada mensaje (exitoso/fallido)
- **Telemetría**: Estadísticas de uso y rendimiento

## ⚠️ Advertencias Importantes

1. **Uso Responsable:** Este bot está diseñado para uso legítimo. No lo uses para spam o mensajes no solicitados.
2. **Límites de WhatsApp:** WhatsApp puede bloquear temporalmente tu cuenta si detecta actividad inusual.
3. **Respeta la privacidad:** Solo envía mensajes a contactos que hayan dado su consentimiento.

## 🤝 Contribuciones

Las contribuciones son bienvenidas. Por favor:
1. Haz un fork del proyecto
2. Crea una rama para tu feature (`git checkout -b feature/nueva-funcionalidad`)
3. Commit tus cambios (`git commit -m 'Añade nueva funcionalidad'`)
4. Push a la rama (`git push origin feature/nueva-funcionalidad`)
5. Abre un Pull Request

## 📄 Licencia

Este proyecto está bajo una licencia de código abierto. Consulta el archivo LICENSE para más detalles.

## 💬 Soporte

Si encuentras algún problema o tienes preguntas:
- Abre un issue en el repositorio
- Revisa los logs en la carpeta `logs/`
- Consulta la documentación de las librerías utilizadas

---

**Desarrollado con ❤️ para automatizar tu comunicación en WhatsApp**
