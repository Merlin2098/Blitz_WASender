# 🧩 Matrix File Processor v2.0

> **Aplicación de escritorio para procesamiento masivo de PDFs** - Divide, renombra y organiza documentos de manera automática con interfaz moderna y temas personalizables.

![Python](https://img.shields.io/badge/Python-3.8+-blue.svg)
![License](https://img.shields.io/badge/License-MIT-green.svg)
![Platform](https://img.shields.io/badge/Platform-Windows-lightgrey.svg)

---

## 📋 Tabla de Contenidos

- [Características](#-características)
- [Requisitos](#-requisitos)
- [Instalación](#-instalación)
- [Uso](#-uso)
- [Estructura del Proyecto](#-estructura-del-proyecto)
- [Generación de Ejecutable](#-generación-de-ejecutable)
- [Temas Personalizables](#-temas-personalizables)
- [Optimizaciones](#-optimizaciones)
- [Contribuir](#-contribuir)
- [Licencia](#-licencia)

---

## ✨ Características

### 📄 Divisor de PDFs
- Divide archivos PDF grandes en múltiples archivos más pequeños
- Configuración personalizada de hojas por archivo
- Validación automática de divisibilidad exacta

### 🧾 Renombrado Inteligente
Procesa y renombra automáticamente:
- **Boletas de Pago**: Extrae nombre, DNI y fecha de ingreso
- **Certificados AFP**: Identifica titular y DNI del certificado
- **Quinta Categoría**: Procesa certificados de rentas con paralelización
- **SUNAT (CIR)**: Renombra documentos ALTA/BAJA con fechas

### 🛠️ Herramientas Adicionales
- **Limpiador de Duplicados**: Detecta y elimina archivos duplicados por DNI
- **Reporte de Errores**: Genera archivos Excel con errores encontrados
- **Procesamiento Paralelo**: Utiliza ThreadPoolExecutor para máxima velocidad

### 🎨 Interfaz Moderna
- Temas claro y oscuro con persistencia
- Barra de progreso inteligente (actualización cada 2%)
- Consola en tiempo real (buffer optimizado cada 4s)
- Métricas en vivo (archivos procesados y tiempo)
- Sistema de sonidos para feedback

---

## 🔧 Requisitos

- **Python**: 3.8 o superior
- **Sistema Operativo**: Windows (optimizado)
- **Dependencias**: Ver `requirements.txt`

### Bibliotecas Principales
```
pdfplumber       # Extracción avanzada de texto desde PDFs
PyPDF2           # Manipulación de archivos PDF
openpyxl         # Generación de reportes Excel
psutil           # Monitoreo de recursos del sistema
tkinter          # Interfaz gráfica (incluida en Python)
```

---

## 📦 Instalación

### 1. Clonar el Repositorio
```bash
git clone https://github.com/tu-usuario/matrix-file-processor.git
cd matrix-file-processor
```

### 2. Crear Entorno Virtual
```bash
python -m venv venv
venv\Scripts\activate  # Windows
```

### 3. Instalar Dependencias
```bash
pip install -r requirements.txt
```

### 4. Ejecutar la Aplicación
```bash
python main.py
```

---

## 🚀 Uso

### Modo Interfaz Gráfica

1. **Ejecuta el programa**:
   ```bash
   python main.py
   ```

2. **Dividir PDFs**:
   - Pestaña "DIVIDIR PDF"
   - Selecciona archivo PDF
   - Define hojas por archivo
   - Presiona "DIVIDIR PDF"

3. **Renombrar Documentos**:
   - Pestaña "RENOMBRAR"
   - Selecciona tipo de documento
   - Elige carpeta o archivo
   - Presiona "EJECUTAR"

4. **Limpiar Duplicados**:
   - Pestaña "HERRAMIENTAS"
   - Selecciona carpeta procesada
   - Presiona "LIMPIAR DUPLICADOS"

### Modo Consola (Scripts Individuales)

```bash
# Dividir PDF
python dividir_pdf.py

# Renombrar boletas
python boletas.py

# Certificados AFP
python afp_rename.py

# Quinta categoría
python quinta_rename.py

# SUNAT
python sunat.py

# Eliminar duplicados
python sunat_duplicados.py
```

---

## 📁 Estructura del Proyecto

```
matrix-file-processor/
│
├── main.py                  # Aplicación principal Tkinter
├── dividir_pdf.py           # Módulo divisor de PDFs
├── boletas.py               # Renombrador de boletas
├── afp_rename.py            # Renombrador certificados AFP
├── quinta_rename.py         # Renombrador quinta categoría
├── sunat.py                 # Renombrador SUNAT (CIR)
├── sunat_duplicados.py      # Limpiador de duplicados
├── theme_manager.py         # Gestor de temas claro/oscuro
├── theme_config.json        # Persistencia de preferencias
├── 1.generar.py             # Generador de ejecutable
├── requirements.txt         # Dependencias del proyecto
└── README.md                # Este archivo
```

---

## 🏗️ Generación de Ejecutable

El proyecto incluye un script automatizado para generar el ejecutable con **PyInstaller**.

### Pasos para Generar el .exe

1. **Activa el entorno virtual**:
   ```bash
   venv\Scripts\activate
   ```

2. **Ejecuta el generador**:
   ```bash
   python 1.generar.py
   ```

3. **Sigue las instrucciones**:
   - Valida el entorno virtual
   - Revisa las librerías instaladas
   - Confirma la generación
   - Espera la compilación

4. **Encuentra tu ejecutable**:
   ```
   dist/MatrixFileProcessor/MatrixFileProcessor.exe
   ```

### Características del Ejecutable
- **Modo OneDiR**: Carpeta con todas las dependencias
- **Sin consola**: Interfaz limpia sin ventana CMD
- **Librerías excluidas**: Optimizado (sin pip, setuptools, etc.)
- **Listo para distribuir**: Solo comparte la carpeta completa

---

## 🎨 Temas Personalizables

El sistema soporta dos temas con persistencia automática:

### Tema Oscuro (Matrix)
- Fondo negro (#000000)
- Texto verde Matrix (#00FF00)
- Estilo hacker/terminal

### Tema Claro (Profesional)
- Fondo gris claro (#F8FAFC)
- Texto azul marino (#0F172A)
- Estilo corporativo moderno

**Cambio de tema**: Botón "🌙/☀️ Cambiar tema" en la esquina superior izquierda

---

## ⚡ Optimizaciones

### Rendimiento
- **Buffer de Consola**: Actualización cada 4 segundos (reduce redraws)
- **Barra de Progreso**: Actualización cada 2% (evita saturación)
- **Procesamiento Paralelo**: ThreadPoolExecutor con 4 workers
- **Prioridad CPU**: Configurable (NORMAL por defecto)

### Gestión de Recursos
- Monitoreo de CPU y RAM con `psutil`
- Límite de 80% CPU / 90% RAM (configurable)
- Pausa automática si se exceden límites

### Manejo de Errores
- Sistema de reporte Excel automático
- Logs detallados con timestamps
- Recuperación ante fallos individuales

---

## 🤝 Contribuir

Las contribuciones son bienvenidas. Por favor:

1. Fork el proyecto
2. Crea una rama para tu feature (`git checkout -b feature/AmazingFeature`)
3. Commit tus cambios (`git commit -m 'Add: nueva funcionalidad'`)
4. Push a la rama (`git push origin feature/AmazingFeature`)
5. Abre un Pull Request

---

## 📝 Notas Importantes

- Los archivos procesados se renombran **en la misma ubicación** (no se crean copias)
- Siempre se conserva un backup del nombre original en caso de duplicados
- Los reportes de errores se generan automáticamente en formato Excel
- El tema seleccionado se guarda en `theme_config.json`

---

## 🐛 Solución de Problemas

### Error: "No se encontró el archivo PDF"
- Verifica que la ruta no contenga caracteres especiales
- Asegúrate de que el archivo exista y sea un PDF válido

### Error: "No se pudo extraer datos"
- El PDF puede estar escaneado (sin texto extraíble)
- El formato del documento no coincide con el patrón esperado

### Bajo rendimiento
- Reduce `max_workers` en los scripts paralelos
- Cierra otras aplicaciones que consuman recursos
- Procesa lotes más pequeños de archivos

---

## 📄 Licencia

Este proyecto está licenciado bajo la Licencia MIT - ver el archivo [LICENSE](LICENSE) para más detalles.

---

⭐ **Si este proyecto te fue útil, considera darle una estrella en GitHub**