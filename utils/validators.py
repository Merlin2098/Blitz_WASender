"""
Módulo de validaciones
Funciones para validar archivos, rutas, números y estructura de Excel
"""

import os
import re
from pathlib import Path


def validar_archivo_existe(ruta):
    """
    Valida que un archivo exista.
    
    Args:
        ruta (str): Ruta del archivo
    
    Returns:
        tuple: (bool, str) - (éxito, mensaje)
    """
    if not ruta or ruta.strip() == "":
        return False, "Ruta vacía"
    
    if not os.path.exists(ruta):
        return False, f"El archivo no existe: {ruta}"
    
    if not os.path.isfile(ruta):
        return False, f"La ruta no es un archivo: {ruta}"
    
    return True, "Archivo válido"


def validar_extension(ruta, extensiones_validas):
    """
    Valida que un archivo tenga una extensión válida.
    
    Args:
        ruta (str): Ruta del archivo
        extensiones_validas (list): Lista de extensiones válidas (ej: ['.xlsx', '.xls'])
    
    Returns:
        tuple: (bool, str) - (éxito, mensaje)
    """
    if not ruta:
        return False, "Ruta vacía"
    
    extension = Path(ruta).suffix.lower()
    
    if extension not in extensiones_validas:
        return False, f"Extensión inválida. Se esperaba: {', '.join(extensiones_validas)}"
    
    return True, f"Extensión válida: {extension}"


def validar_numero_telefono(codigo_pais, numero):
    """
    Valida que un número de teléfono sea válido.
    
    Args:
        codigo_pais (str/int): Código de país
        numero (str/int): Número de teléfono
    
    Returns:
        tuple: (bool, str, str) - (éxito, mensaje, número_completo)
    """
    # Convertir a string y limpiar
    codigo_pais = str(codigo_pais).strip()
    numero = str(numero).strip()
    
    # Validar que solo contengan dígitos
    if not codigo_pais.isdigit():
        return False, "Código de país debe contener solo dígitos", None
    
    if not numero.isdigit():
        return False, "Número debe contener solo dígitos", None
    
    # Validar longitud del código de país (1-3 dígitos)
    if len(codigo_pais) < 1 or len(codigo_pais) > 3:
        return False, "Código de país debe tener entre 1 y 3 dígitos", None
    
    # Validar longitud del número (6-15 dígitos según estándar internacional)
    if len(numero) < 6 or len(numero) > 15:
        return False, "Número debe tener entre 6 y 15 dígitos", None
    
    # Construir número completo
    numero_completo = codigo_pais + numero
    
    return True, "Número válido", numero_completo


def validar_estructura_excel(ruta):
    """
    Valida que un archivo Excel tenga la estructura correcta.
    
    Args:
        ruta (str): Ruta del archivo Excel
    
    Returns:
        tuple: (bool, str, dict) - (éxito, mensaje, info_hojas)
    """
    try:
        import pandas as pd
    except ImportError:
        return False, "pandas no está instalado. Ejecuta: pip install pandas openpyxl", None
    
    # Validar que el archivo exista y sea Excel
    existe, msg = validar_archivo_existe(ruta)
    if not existe:
        return False, msg, None
    
    es_excel, msg = validar_extension(ruta, ['.xlsx', '.xls'])
    if not es_excel:
        return False, msg, None
    
    try:
        # Leer nombres de hojas
        excel_file = pd.ExcelFile(ruta)
        hojas_disponibles = excel_file.sheet_names
        
        # Validar que existan las hojas requeridas
        hojas_requeridas = ['Mensajes', 'Contactos']
        hojas_faltantes = [h for h in hojas_requeridas if h not in hojas_disponibles]
        
        if hojas_faltantes:
            return False, f"Faltan hojas requeridas: {', '.join(hojas_faltantes)}", None
        
        # Validar columnas en hoja "Mensajes"
        df_mensajes = pd.read_excel(ruta, sheet_name='Mensajes')
        columnas_mensajes_req = ['ID_Mensaje', 'Mensaje']
        columnas_mensajes_faltantes = [c for c in columnas_mensajes_req if c not in df_mensajes.columns]
        
        if columnas_mensajes_faltantes:
            return False, f"Hoja 'Mensajes' - Faltan columnas: {', '.join(columnas_mensajes_faltantes)}", None
        
        # Validar columnas en hoja "Contactos"
        df_contactos = pd.read_excel(ruta, sheet_name='Contactos')
        columnas_contactos_req = ['Destinatario', 'Codigo_Pais', 'Numero', 'Remitente', 'ID_Mensaje']
        columnas_contactos_faltantes = [c for c in columnas_contactos_req if c not in df_contactos.columns]
        
        if columnas_contactos_faltantes:
            return False, f"Hoja 'Contactos' - Faltan columnas: {', '.join(columnas_contactos_faltantes)}", None
        
        # Información de las hojas
        info_hojas = {
            'mensajes': {
                'filas': len(df_mensajes),
                'columnas': list(df_mensajes.columns)
            },
            'contactos': {
                'filas': len(df_contactos),
                'columnas': list(df_contactos.columns)
            }
        }
        
        return True, "Estructura de Excel válida", info_hojas
        
    except Exception as e:
        return False, f"Error al leer Excel: {str(e)}", None


def validar_id_mensaje_existe(id_mensaje, mensajes_dict):
    """
    Valida que un ID_Mensaje exista en el diccionario de mensajes.
    
    Args:
        id_mensaje (int): ID del mensaje a buscar
        mensajes_dict (dict): Diccionario de mensajes {ID_Mensaje: {...}}
    
    Returns:
        tuple: (bool, str) - (éxito, mensaje)
    """
    if id_mensaje not in mensajes_dict:
        return False, f"ID_Mensaje {id_mensaje} no existe en la hoja Mensajes"
    
    return True, "ID_Mensaje válido"


def validar_campos_mensaje(mensaje):
    """
    Valida un mensaje y extrae los campos dinámicos (entre llaves).
    Los campos son opcionales - el mensaje puede no tener ninguno.
    
    Args:
        mensaje (str): Texto del mensaje
    
    Returns:
        tuple: (bool, str, list) - (éxito, mensaje, campos_encontrados)
    """
    if not mensaje or str(mensaje).strip() == "":
        return False, "Mensaje vacío", []
    
    # Buscar campos entre llaves
    campos = re.findall(r'\{(\w+)\}', str(mensaje))
    
    # Los campos son opcionales, solo informamos cuáles se encontraron
    if campos:
        campos_info = f"Campos encontrados: {', '.join(['{' + c + '}' for c in campos])}"
    else:
        campos_info = "Sin campos dinámicos"
    
    return True, campos_info, campos