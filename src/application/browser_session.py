from __future__ import annotations

from src.infrastructure.browser import BrowserDriverFactory


class BrowserSessionService:
    """
    Caso de uso para perfiles y sesiones manuales del navegador.
    """

    def __init__(self, driver_factory: BrowserDriverFactory | None = None):
        self.driver_factory = driver_factory or BrowserDriverFactory()

    def ensure_profile(self, navegador: str) -> str:
        return self.driver_factory.ensure_profile_dir(navegador)

    def initialize_driver(self, navegador: str):
        return self.driver_factory.create_driver(navegador)

    def launch_whatsapp_for_sync(self, navegador: str):
        driver = self.initialize_driver(navegador)
        driver.get("https://web.whatsapp.com")
        return driver
