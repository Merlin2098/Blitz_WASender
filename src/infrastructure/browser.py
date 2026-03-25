from __future__ import annotations

from selenium import webdriver
from selenium.webdriver.chrome.options import Options as ChromeOptions
from selenium.webdriver.edge.options import Options as EdgeOptions
from selenium.webdriver.firefox.options import Options as FirefoxOptions

from .paths import AppPaths


class BrowserDriverFactory:
    """
    Construcción unificada de WebDrivers y perfiles aislados.
    """

    def __init__(self, paths: AppPaths | None = None):
        self.paths = paths or AppPaths()

    def get_profile_dir(self, navegador: str) -> str:
        return self.paths.get_profile_dir(navegador)

    def ensure_profile_dir(self, navegador: str) -> str:
        return self.get_profile_dir(navegador)

    def create_driver(self, navegador: str):
        navegador = navegador.lower()
        ruta_perfil = self.get_profile_dir(navegador)

        if navegador == "edge":
            options = EdgeOptions()
            options.add_argument(f"user-data-dir={ruta_perfil}")
            options.add_argument("--start-maximized")
            options.add_argument("--disable-blink-features=AutomationControlled")
            options.add_experimental_option("excludeSwitches", ["enable-automation"])
            options.add_experimental_option("useAutomationExtension", False)
            return webdriver.Edge(options=options)

        if navegador == "chrome":
            options = ChromeOptions()
            options.add_argument(f"user-data-dir={ruta_perfil}")
            options.add_argument("--start-maximized")
            options.add_argument("--disable-blink-features=AutomationControlled")
            options.add_experimental_option("excludeSwitches", ["enable-automation"])
            options.add_experimental_option("useAutomationExtension", False)
            return webdriver.Chrome(options=options)

        if navegador == "firefox":
            options = FirefoxOptions()
            options.add_argument("-profile")
            options.add_argument(ruta_perfil)
            options.set_preference("dom.webdriver.enabled", False)
            options.set_preference("useAutomationExtension", False)
            driver = webdriver.Firefox(options=options)
            driver.maximize_window()
            return driver

        raise ValueError(f"Navegador no soportado: {navegador}")
