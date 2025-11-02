"""
Módulo para envío de mensajes por WhatsApp Web
Clase WhatsAppSender que maneja toda la lógica de envío

SPRINT 1: Agregado soporte para logger con naming dinámico
LÓGICA DE ENVÍO: Mantenida 100% intacta (URL + Enter)
"""

import time
import random
import urllib.parse
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException, NoSuchElementException


class WhatsAppSender:
    """
    Clase para enviar mensajes masivos por WhatsApp Web usando Selenium.
    
    SPRINT 1: Compatible con logger mejorado
    """
    
    def __init__(self, driver, logger=None, delay_min=15, delay_max=22):
        """
        Inicializa el sender de WhatsApp.
        
        Args:
            driver: WebDriver de Selenium
            logger: Logger para registrar eventos (opcional)
            delay_min (int): Delay mínimo entre mensajes en segundos (default: 15)
            delay_max (int): Delay máximo entre mensajes en segundos (default: 22)
        """
        self.driver = driver
        self.logger = logger
        self.delay_min = delay_min
        self.delay_max = delay_max
        self.wait = WebDriverWait(driver, 20)
        
        if self.logger:
            self.logger.info("WhatsAppSender inicializado")
            self.logger.info(f"Delay entre mensajes: {delay_min}-{delay_max} segundos")
    
    
    def esperar_carga_whatsapp(self, timeout=30):
        """
        Espera a que WhatsApp Web cargue completamente.
        
        Args:
            timeout (int): Tiempo máximo de espera en segundos
        
        Returns:
            bool: True si cargó correctamente, False si hubo error
        """
        try:
            if self.logger:
                self.logger.info("Esperando carga de WhatsApp Web...")
            
            # Esperar a que aparezca el elemento de búsqueda (indica que está logueado)
            self.wait.until(
                EC.presence_of_element_located((By.XPATH, "//div[@contenteditable='true'][@data-tab='3']"))
            )
            
            if self.logger:
                self.logger.info("✓ WhatsApp Web cargado correctamente")
            return True
            
        except TimeoutException:
            if self.logger:
                self.logger.error("✗ Timeout: WhatsApp Web no cargó a tiempo")
                self.logger.error("Verifica que hayas escaneado el código QR")
            return False
        except Exception as e:
            if self.logger:
                self.logger.error(f"✗ Error al cargar WhatsApp Web: {str(e)}")
            return False
    
    
    def construir_url_whatsapp(self, codigo_pais, numero, mensaje=""):
        """
        Construye la URL de WhatsApp con el número y mensaje.
        
        Args:
            codigo_pais (str): Código de país
            numero (str): Número de teléfono
            mensaje (str): Mensaje a enviar (opcional)
        
        Returns:
            str: URL completa de WhatsApp
        """
        numero_completo = f"{codigo_pais}{numero}"
        
        if mensaje:
            # Codificar mensaje para URL
            mensaje_encoded = urllib.parse.quote(mensaje)
            url = f"https://web.whatsapp.com/send?phone={numero_completo}&text={mensaje_encoded}"
        else:
            url = f"https://web.whatsapp.com/send?phone={numero_completo}"
        
        return url
    
    
    def navegar_a_contacto(self, codigo_pais, numero, mensaje=""):
        """
        Navega al chat del contacto usando la URL de WhatsApp.
        
        LÓGICA ORIGINAL: Usa URL directa (NO modificar)
        
        Args:
            codigo_pais (str): Código de país
            numero (str): Número de teléfono
            mensaje (str): Mensaje prellenado (opcional)
        
        Returns:
            bool: True si navegó correctamente, False si hubo error
        """
        try:
            url = self.construir_url_whatsapp(codigo_pais, numero, mensaje)
            if self.logger:
                self.logger.info(f"Navegando al chat: +{codigo_pais}{numero}")
            
            self.driver.get(url)
            time.sleep(3)  # Esperar carga inicial
            
            # Verificar si el número es inválido
            try:
                error_element = self.driver.find_element(By.XPATH, "//*[contains(text(), 'Número de teléfono compartido a través de url no válido')]")
                if self.logger:
                    self.logger.error(f"✗ Número inválido: +{codigo_pais}{numero}")
                return False
            except NoSuchElementException:
                pass  # No hay error, continuar
            
            # Esperar a que cargue el chat
            self.wait.until(
                EC.presence_of_element_located((By.XPATH, "//div[@contenteditable='true'][@data-tab='10']"))
            )
            
            if self.logger:
                self.logger.info(f"✓ Chat abierto correctamente")
            return True
            
        except TimeoutException:
            if self.logger:
                self.logger.error(f"✗ Timeout al abrir chat de +{codigo_pais}{numero}")
            return False
        except Exception as e:
            if self.logger:
                self.logger.error(f"✗ Error al navegar al contacto: {str(e)}")
            return False
    
    
    def enviar_mensaje_actual(self):
        """
        Envía el mensaje presionando Enter en el campo de texto.
        
        LÓGICA ORIGINAL: Presiona Enter para enviar (NO modificar)
        
        Returns:
            bool: True si envió correctamente, False si hubo error
        """
        try:
            # Buscar el campo de texto del mensaje
            campo_mensaje = self.wait.until(
                EC.presence_of_element_located((By.XPATH, "//div[@contenteditable='true'][@data-tab='10']"))
            )
            
            # Presionar Enter para enviar
            campo_mensaje.send_keys(Keys.ENTER)
            if self.logger:
                self.logger.info("✓ Mensaje enviado (Enter)")
            
            # Esperar confirmación (palomita doble)
            time.sleep(2)
            
            return True
            
        except TimeoutException:
            if self.logger:
                self.logger.error("✗ Timeout al enviar mensaje")
            return False
        except Exception as e:
            if self.logger:
                self.logger.error(f"✗ Error al enviar mensaje: {str(e)}")
            return False
    
    
    def enviar_mensaje(self, codigo_pais, numero, mensaje):
        """
        Envía un mensaje de texto a un contacto.
        
        LÓGICA ORIGINAL: URL directa + Enter (NO modificar)
        SPRINT 1: Retorna telemetría básica
        
        Args:
            codigo_pais (str): Código de país
            numero (str): Número de teléfono
            mensaje (str): Mensaje a enviar
        
        Returns:
            tuple: (bool, str) - (éxito, mensaje_resultado)
        """
        try:
            import time
            tiempo_inicio = time.time()
            
            # Navegar al contacto con mensaje prellenado
            if not self.navegar_a_contacto(codigo_pais, numero, mensaje):
                tiempo_fin = time.time()
                tiempo_envio = round(tiempo_fin - tiempo_inicio, 2)
                return False, "Error al abrir chat"
            
            # Enviar mensaje
            if not self.enviar_mensaje_actual():
                tiempo_fin = time.time()
                tiempo_envio = round(tiempo_fin - tiempo_inicio, 2)
                return False, "Error al enviar mensaje"
            
            tiempo_fin = time.time()
            tiempo_envio = round(tiempo_fin - tiempo_inicio, 2)
            
            if self.logger:
                self.logger.info(f"✓✓ Mensaje enviado exitosamente a +{codigo_pais}{numero}")
                self.logger.info(f"   Tiempo de envío: {tiempo_envio}s")
            
            return True, "Enviado correctamente"
            
        except Exception as e:
            error_msg = f"Error general: {str(e)}"
            if self.logger:
                self.logger.error(f"✗ {error_msg}")
            return False, error_msg
    
    
    def aplicar_delay_aleatorio(self):
        """
        Aplica un delay aleatorio entre mensajes para evitar detección.
        """
        delay = random.randint(self.delay_min, self.delay_max)
        if self.logger:
            self.logger.info(f"Esperando {delay} segundos antes del siguiente mensaje...")
        
        for i in range(delay, 0, -1):
            print(f"\rEsperando: {i} segundos restantes...", end='', flush=True)
            time.sleep(1)
        
        print("\r" + " " * 50 + "\r", end='', flush=True)  # Limpiar línea
        if self.logger:
            self.logger.info("Delay completado, continuando...")
    
    
    def verificar_sesion_activa(self):
        """
        Verifica si la sesión de WhatsApp Web está activa.
        
        Returns:
            bool: True si está activa, False si no
        """
        try:
            # Buscar elemento que solo aparece cuando está logueado
            self.driver.find_element(By.XPATH, "//div[@contenteditable='true'][@data-tab='3']")
            return True
        except NoSuchElementException:
            return False
        except Exception as e:
            if self.logger:
                self.logger.error(f"Error al verificar sesión: {str(e)}")
            return False