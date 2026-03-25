"""
Módulo para envío de mensajes por WhatsApp Web
Clase WhatsAppSender que maneja toda la lógica de envío

SPRINT 1: Agregado soporte para logger con naming dinámico
LÓGICA DE ENVÍO: Mantenida 100% intacta (URL + Enter)
"""

import time
import random
import urllib.parse
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support.ui import WebDriverWait
from selenium.common.exceptions import TimeoutException, NoSuchElementException

from .locators import (
    MESSAGE_COMPOSER_LOCATORS,
    OPEN_CHAT_LOCATORS,
    SEND_BUTTON_LOCATORS,
    SESSION_ACTIVE_LOCATORS,
)


class WhatsAppWebClient:
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

    def _primer_elemento_disponible(self, localizadores, timeout=20):
        """
        Retorna el primer elemento disponible entre varios localizadores.
        """
        wait = WebDriverWait(self.driver, timeout)

        def buscar(driver):
            for by, value in localizadores:
                elementos = driver.find_elements(by, value)
                for elemento in elementos:
                    try:
                        if elemento.is_displayed():
                            return elemento
                    except Exception:
                        continue
            return False

        return wait.until(buscar)

    def _elemento_visible_opcional(self, localizadores):
        """
        Retorna el primer elemento visible encontrado o None si no existe.
        """
        for by, value in localizadores:
            elementos = self.driver.find_elements(by, value)
            for elemento in elementos:
                try:
                    if elemento.is_displayed():
                        return elemento
                except Exception:
                    continue
        return None

    def wait_until_ready(self, timeout=30):
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

            self._primer_elemento_disponible(SESSION_ACTIVE_LOCATORS, timeout=timeout)
            
            if self.logger:
                self.logger.info("✓ WhatsApp Web cargado correctamente")
            return True
            
        except TimeoutException:
            if self.logger:
                self.logger.error("✗ Timeout: WhatsApp Web no cargó a tiempo")
                self.logger.error(f"Título detectado: {self.driver.title}")
                self.logger.error(f"URL detectada: {self.driver.current_url}")
                self.logger.error("WhatsApp Web puede haber cargado, pero los selectores de sesión no coincidieron")
            return False
        except Exception as e:
            if self.logger:
                self.logger.error(f"✗ Error al cargar WhatsApp Web: {str(e)}")
            return False
    
    
    def build_send_url(self, codigo_pais, numero, mensaje=""):
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
    
    
    def open_chat(self, codigo_pais, numero, mensaje=""):
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
            url = self.build_send_url(codigo_pais, numero, mensaje)
            if self.logger:
                self.logger.info(f"Navegando al chat: +{codigo_pais}{numero}")
            
            self.driver.get(url)
            time.sleep(3)  # Esperar carga inicial
            
            # Verificar si el número es inválido
            try:
                error_element = self.driver.find_element("xpath", "//*[contains(text(), 'Número de teléfono compartido a través de url no válido')]")
                if self.logger:
                    self.logger.error(f"✗ Número inválido: +{codigo_pais}{numero}")
                return False
            except NoSuchElementException:
                pass  # No hay error, continuar
            
            # Esperar a que cargue el chat o el área principal de conversación
            self._primer_elemento_disponible(OPEN_CHAT_LOCATORS, timeout=20)
            
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
    
    
    def send_current_message(self):
        """
        Envía el mensaje presionando Enter en el campo de texto.
        
        LÓGICA ORIGINAL: Presiona Enter para enviar (NO modificar)
        
        Returns:
            bool: True si envió correctamente, False si hubo error
        """
        try:
            # Buscar el campo de texto del mensaje con selectores más robustos
            campo_mensaje = self._primer_elemento_disponible(MESSAGE_COMPOSER_LOCATORS, timeout=20)

            # Mantener foco explícito en el compositor antes del envío.
            try:
                campo_mensaje.click()
            except Exception:
                pass
            
            # Presionar Enter para enviar
            campo_mensaje.send_keys(Keys.ENTER)
            
            # Si el botón de enviar sigue visible, Enter no bastó: usar fallback por click.
            time.sleep(1)
            boton_enviar = self._elemento_visible_opcional(SEND_BUTTON_LOCATORS)
            if boton_enviar is not None:
                boton_enviar.click()
                if self.logger:
                    self.logger.info("✓ Mensaje enviado (fallback botón Enviar)")
            else:
                if self.logger:
                    self.logger.info("✓ Mensaje enviado (Enter)")

            time.sleep(1)
            
            return True
            
        except TimeoutException:
            if self.logger:
                self.logger.error("✗ Timeout al enviar mensaje")
            return False
        except Exception as e:
            if self.logger:
                self.logger.error(f"✗ Error al enviar mensaje: {str(e)}")
            return False
    
    
    def send_prefilled_message(self, codigo_pais, numero, mensaje):
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
            if not self.open_chat(codigo_pais, numero, mensaje):
                tiempo_fin = time.time()
                tiempo_envio = round(tiempo_fin - tiempo_inicio, 2)
                return False, "Error al abrir chat"
            
            # Enviar mensaje
            if not self.send_current_message():
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
    
    
    def apply_random_delay(self):
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
    
    
    def is_session_active(self):
        """
        Verifica si la sesión de WhatsApp Web está activa.
        
        Returns:
            bool: True si está activa, False si no
        """
        try:
            self._primer_elemento_disponible(SESSION_ACTIVE_LOCATORS, timeout=5)
            return True
        except TimeoutException:
            return False
        except Exception as e:
            if self.logger:
                self.logger.error(f"Error al verificar sesión: {str(e)}")
            return False

    # Compatibilidad temporal
    def esperar_carga_whatsapp(self, timeout=30):
        return self.wait_until_ready(timeout=timeout)

    def construir_url_whatsapp(self, codigo_pais, numero, mensaje=""):
        return self.build_send_url(codigo_pais, numero, mensaje)

    def navegar_a_contacto(self, codigo_pais, numero, mensaje=""):
        return self.open_chat(codigo_pais, numero, mensaje)

    def enviar_mensaje_actual(self):
        return self.send_current_message()

    def enviar_mensaje(self, codigo_pais, numero, mensaje):
        return self.send_prefilled_message(codigo_pais, numero, mensaje)

    def aplicar_delay_aleatorio(self):
        return self.apply_random_delay()

    def verificar_sesion_activa(self):
        return self.is_session_active()


WhatsAppSender = WhatsAppWebClient
