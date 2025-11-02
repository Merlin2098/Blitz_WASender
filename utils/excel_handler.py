"""
Módulo para manejo de archivos Excel
Lectura, validación y generación de reportes
VERSIÓN SPRINT 1: Telemetría + naming dinámico DD.MM.YYYY_HH.MM.SS
"""

import pandas as pd
import os
import time
from datetime import datetime


def validar_hojas(ruta_excel):
    """
    Valida que el Excel tenga las hojas requeridas.
    
    Args:
        ruta_excel (str): Ruta del archivo Excel
    
    Returns:
        tuple: (bool, str, list) - (éxito, mensaje, hojas_disponibles)
    """
    try:
        excel_file = pd.ExcelFile(ruta_excel)
        hojas_disponibles = excel_file.sheet_names
        
        hojas_requeridas = ['Mensajes', 'Contactos']
        hojas_faltantes = [h for h in hojas_requeridas if h not in hojas_disponibles]
        
        if hojas_faltantes:
            return False, f"Faltan hojas: {', '.join(hojas_faltantes)}", hojas_disponibles
        
        return True, "Todas las hojas requeridas están presentes", hojas_disponibles
        
    except Exception as e:
        return False, f"Error al leer Excel: {str(e)}", []


def leer_mensajes(ruta_excel, logger=None):
    """
    Lee la hoja "Mensajes" y retorna un diccionario.
    
    Args:
        ruta_excel (str): Ruta del archivo Excel
        logger: Logger opcional para registrar el proceso
    
    Returns:
        dict: {ID_Mensaje: {'mensaje': str}}
    """
    try:
        df = pd.read_excel(ruta_excel, sheet_name='Mensajes')
        
        if logger:
            logger.info(f"Leyendo hoja 'Mensajes': {len(df)} registros encontrados")
        
        # Convertir a diccionario
        mensajes_dict = {}
        
        for index, row in df.iterrows():
            id_mensaje = int(row['ID_Mensaje'])
            mensaje = str(row['Mensaje']).strip()
            
            # Validar que no esté vacío el mensaje
            if not mensaje or mensaje == 'nan':
                if logger:
                    logger.warning(f"Fila {index + 2}: Mensaje vacío para ID_Mensaje {id_mensaje}")
                continue
            
            mensajes_dict[id_mensaje] = {
                'mensaje': mensaje
            }
            
            if logger:
                logger.info(f"  ID {id_mensaje}: cargado")
        
        if logger:
            logger.info(f"Total de mensajes válidos: {len(mensajes_dict)}")
        
        return mensajes_dict
        
    except Exception as e:
        if logger:
            logger.error(f"Error al leer hoja 'Mensajes': {str(e)}")
        raise


def leer_contactos(ruta_excel, logger=None):
    """
    Lee la hoja "Contactos" y retorna una lista de diccionarios.
    
    Args:
        ruta_excel (str): Ruta del archivo Excel
        logger: Logger opcional para registrar el proceso
    
    Returns:
        list: Lista de diccionarios con datos de contactos
    """
    try:
        df = pd.read_excel(ruta_excel, sheet_name='Contactos')
        
        if logger:
            logger.info(f"Leyendo hoja 'Contactos': {len(df)} registros encontrados")
        
        contactos = []
        
        for index, row in df.iterrows():
            # Saltar filas vacías
            if pd.isna(row['Destinatario']) or pd.isna(row['Numero']):
                if logger:
                    logger.warning(f"Fila {index + 2}: Datos incompletos, omitiendo...")
                continue
            
            contacto = {
                'fila': index + 2,  # +2 porque Excel empieza en 1 y tiene encabezado
                'destinatario': str(row['Destinatario']).strip(),
                'codigo_pais': str(int(row['Codigo_Pais'])) if pd.notna(row['Codigo_Pais']) else "",
                'numero': str(int(row['Numero'])) if pd.notna(row['Numero']) else "",
                'remitente': str(row['Remitente']).strip() if pd.notna(row['Remitente']) else "",
                'id_mensaje': int(row['ID_Mensaje']) if pd.notna(row['ID_Mensaje']) else None
            }
            
            contactos.append(contacto)
        
        if logger:
            logger.info(f"Total de contactos válidos: {len(contactos)}")
        
        return contactos
        
    except Exception as e:
        if logger:
            logger.error(f"Error al leer hoja 'Contactos': {str(e)}")
        raise


def validar_columnas(df, columnas_requeridas):
    """
    Valida que un DataFrame tenga las columnas requeridas.
    
    Args:
        df (pd.DataFrame): DataFrame a validar
        columnas_requeridas (list): Lista de nombres de columnas requeridas
    
    Returns:
        tuple: (bool, list) - (todas_presentes, columnas_faltantes)
    """
    columnas_faltantes = [col for col in columnas_requeridas if col not in df.columns]
    return len(columnas_faltantes) == 0, columnas_faltantes


def generar_reporte(datos_envio, carpeta="reportes", nombre_base="reporte_envio"):
    """
    Genera un reporte en Excel con los resultados de los envíos.
    
    Args:
        datos_envio (list): Lista de diccionarios con datos de cada envío
        carpeta (str): Carpeta donde guardar el reporte
        nombre_base (str): Nombre base del archivo
    
    Returns:
        str: Ruta del archivo generado
    """
    # Crear carpeta si no existe
    if not os.path.exists(carpeta):
        os.makedirs(carpeta)
    
    # SPRINT 3.2: Generar nombre con formato nombre_base_dd.mm.yyyy_hh.mm.ss
    timestamp = datetime.now().strftime('%d.%m.%Y_%H.%M.%S')
    nombre_archivo = f"{nombre_base}_{timestamp}.xlsx"
    ruta_reporte = os.path.join(carpeta, nombre_archivo)
    
    # Crear DataFrame
    df = pd.DataFrame(datos_envio)
    
    # Calcular estadísticas
    total = len(df)
    exitosos = len(df[df['estado'] == 'EXITOSO'])
    fallidos = len(df[df['estado'] == 'FALLIDO'])
    
    # Crear estadísticas en un DataFrame separado
    estadisticas = pd.DataFrame({
        'Métrica': ['Total de contactos', 'Enviados exitosamente', 'Fallidos', 'Tasa de éxito'],
        'Valor': [
            total,
            exitosos,
            fallidos,
            f"{(exitosos/total*100):.1f}%" if total > 0 else "0%"
        ]
    })
    
    # Escribir a Excel con múltiples hojas
    with pd.ExcelWriter(ruta_reporte, engine='openpyxl') as writer:
        # Hoja de estadísticas
        estadisticas.to_excel(writer, sheet_name='Estadísticas', index=False)
        
        # Hoja de detalles
        df.to_excel(writer, sheet_name='Detalle de Envíos', index=False)
        
        # Ajustar ancho de columnas
        for sheet_name in writer.sheets:
            worksheet = writer.sheets[sheet_name]
            for column in worksheet.columns:
                max_length = 0
                column_letter = column[0].column_letter
                for cell in column:
                    try:
                        if len(str(cell.value)) > max_length:
                            max_length = len(cell.value)
                    except:
                        pass
                adjusted_width = min(max_length + 2, 50)
                worksheet.column_dimensions[column_letter].width = adjusted_width
    
    return ruta_reporte


def generar_reporte_con_telemetria(datos_envio, carpeta="reportes", nombre_base="reporte_envio"):
    """
    Genera un reporte Excel con telemetría avanzada de los envíos.
    
    CAMBIOS SPRINT 1:
    - Naming dinámico: DD.MM.YYYY_HH.MM.SS
    - 3 columnas adicionales: Metodo_Usado, Tiempo_Envio_Seg, Intentos
    - 3 hojas: Resultados, Resumen, Análisis
    
    Args:
        datos_envio (list): Lista de diccionarios con datos de cada envío
            Debe incluir: 'metodo_usado', 'tiempo_envio', 'intentos'
        carpeta (str): Carpeta donde guardar el reporte
        nombre_base (str): Nombre base del archivo
    
    Returns:
        str: Ruta del archivo generado
    """
    # Crear carpeta si no existe
    if not os.path.exists(carpeta):
        os.makedirs(carpeta)
    
    # SPRINT 3.2: Generar nombre con formato nombre_base_dd.mm.yyyy_hh.mm.ss
    timestamp = datetime.now().strftime('%d.%m.%Y_%H.%M.%S')
    nombre_archivo = f"{nombre_base}_{timestamp}.xlsx"
    ruta_reporte = os.path.join(carpeta, nombre_archivo)
    
    # Crear DataFrame principal
    df = pd.DataFrame(datos_envio)
    
    # Calcular estadísticas generales
    total = len(df)
    exitosos = len(df[df['estado'] == 'EXITOSO'])
    fallidos = len(df[df['estado'] == 'FALLIDO'])
    tasa_exito = (exitosos / total * 100) if total > 0 else 0
    
    # Calcular estadísticas de telemetría
    if 'tiempo_envio' in df.columns and exitosos > 0:
        df_exitosos = df[df['estado'] == 'EXITOSO']
        tiempo_promedio = df_exitosos['tiempo_envio'].mean()
        tiempo_total = df_exitosos['tiempo_envio'].sum()
    else:
        tiempo_promedio = 0
        tiempo_total = 0
    
    if 'intentos' in df.columns and exitosos > 0:
        intentos_promedio = df_exitosos['intentos'].mean()
    else:
        intentos_promedio = 0
    
    # Análisis por método usado
    analisis_metodos = []
    if 'metodo_usado' in df.columns:
        for metodo in df['metodo_usado'].unique():
            df_metodo = df[df['metodo_usado'] == metodo]
            exitosos_metodo = len(df_metodo[df_metodo['estado'] == 'EXITOSO'])
            total_metodo = len(df_metodo)
            tasa_metodo = (exitosos_metodo / total_metodo * 100) if total_metodo > 0 else 0
            
            analisis_metodos.append({
                'Método': metodo,
                'Usos': total_metodo,
                'Exitosos': exitosos_metodo,
                'Tasa_Éxito': f"{tasa_metodo:.1f}%"
            })
    
    df_analisis = pd.DataFrame(analisis_metodos) if analisis_metodos else pd.DataFrame()
    
    # Crear DataFrame de resumen
    estadisticas = pd.DataFrame({
        'Métrica': [
            'Total de contactos',
            'Enviados exitosamente',
            'Fallidos',
            'Tasa de éxito',
            '---TELEMETRÍA---',
            'Tiempo promedio por envío (seg)',
            'Tiempo total de envíos (seg)',
            'Intentos promedio por envío'
        ],
        'Valor': [
            total,
            exitosos,
            fallidos,
            f"{tasa_exito:.1f}%",
            '',
            f"{tiempo_promedio:.2f}" if tiempo_promedio > 0 else "N/A",
            f"{tiempo_total:.2f}" if tiempo_total > 0 else "N/A",
            f"{intentos_promedio:.2f}" if intentos_promedio > 0 else "N/A"
        ]
    })
    
    # Escribir a Excel con múltiples hojas
    with pd.ExcelWriter(ruta_reporte, engine='openpyxl') as writer:
        # HOJA 1: Resultados (datos detallados)
        df.to_excel(writer, sheet_name='Resultados', index=False)
        
        # HOJA 2: Resumen (estadísticas generales)
        estadisticas.to_excel(writer, sheet_name='Resumen', index=False)
        
        # HOJA 3: Análisis (métricas por método)
        if not df_analisis.empty:
            df_analisis.to_excel(writer, sheet_name='Análisis', index=False)
        else:
            # Si no hay datos de análisis, crear hoja vacía con mensaje
            pd.DataFrame({'Mensaje': ['Sin datos de telemetría disponibles']}).to_excel(
                writer, sheet_name='Análisis', index=False
            )
        
        # Ajustar ancho de columnas en todas las hojas
        for sheet_name in writer.sheets:
            worksheet = writer.sheets[sheet_name]
            for column in worksheet.columns:
                max_length = 0
                column_letter = column[0].column_letter
                for cell in column:
                    try:
                        if len(str(cell.value)) > max_length:
                            max_length = len(cell.value)
                    except:
                        pass
                adjusted_width = min(max_length + 2, 50)
                worksheet.column_dimensions[column_letter].width = adjusted_width
    
    return ruta_reporte


def procesar_datos(contactos, mensajes_dict, logger=None):
    """
    Procesa y combina datos de contactos con sus mensajes correspondientes.
    
    Args:
        contactos (list): Lista de contactos
        mensajes_dict (dict): Diccionario de mensajes
        logger: Logger opcional
    
    Returns:
        list: Lista de diccionarios con datos procesados y listos para enviar
    """
    datos_procesados = []
    errores = []
    
    for contacto in contactos:
        try:
            id_mensaje = contacto['id_mensaje']
            
            # Validar que el ID_Mensaje exista
            if id_mensaje not in mensajes_dict:
                error = f"Contacto '{contacto['destinatario']}': ID_Mensaje {id_mensaje} no existe"
                errores.append(error)
                if logger:
                    logger.warning(error)
                continue
            
            # Obtener mensaje
            mensaje_data = mensajes_dict[id_mensaje]
            mensaje = mensaje_data['mensaje']
            
            # Personalizar mensaje (reemplazar solo los campos que existan)
            mensaje_personalizado = mensaje
            
            # Detectar qué campos tiene el mensaje y reemplazarlos
            if '{destinatario}' in mensaje_personalizado:
                mensaje_personalizado = mensaje_personalizado.replace('{destinatario}', contacto['destinatario'])
            
            if '{remitente}' in mensaje_personalizado:
                mensaje_personalizado = mensaje_personalizado.replace('{remitente}', contacto['remitente'])
            
            # Agregar a datos procesados
            datos_procesados.append({
                'fila_excel': contacto['fila'],
                'destinatario': contacto['destinatario'],
                'codigo_pais': contacto['codigo_pais'],
                'numero': contacto['numero'],
                'numero_completo': contacto['codigo_pais'] + contacto['numero'],
                'remitente': contacto['remitente'],
                'mensaje': mensaje_personalizado,
                'id_mensaje': id_mensaje
            })
            
        except Exception as e:
            error = f"Error procesando contacto '{contacto.get('destinatario', 'Desconocido')}': {str(e)}"
            errores.append(error)
            if logger:
                logger.error(error)
    
    if logger:
        logger.info(f"Datos procesados: {len(datos_procesados)} contactos listos")
        if errores:
            logger.warning(f"Errores encontrados: {len(errores)}")
    
    return datos_procesados, errores