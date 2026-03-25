import tempfile
import unittest
from pathlib import Path
from unittest.mock import MagicMock, patch

from src.infrastructure.browser import BrowserDriverFactory
from src.infrastructure.paths import AppPaths


class BrowserDriverFactoryTests(unittest.TestCase):
    def setUp(self):
        self.temp_dir = tempfile.TemporaryDirectory()
        root = Path(self.temp_dir.name)
        anchor = root / "gui_app.py"
        anchor.write_text("# anchor\n", encoding="utf-8")
        self.factory = BrowserDriverFactory(paths=AppPaths(anchor_file=anchor))

    def tearDown(self):
        self.temp_dir.cleanup()

    @patch("src.infrastructure.browser.webdriver.Edge")
    def test_create_edge_driver_uses_isolated_profile(self, edge_driver):
        expected_driver = MagicMock()
        edge_driver.return_value = expected_driver

        driver = self.factory.create_driver("edge")

        self.assertIs(driver, expected_driver)
        options = edge_driver.call_args.kwargs["options"]
        self.assertTrue(any(arg.startswith("user-data-dir=") for arg in options.arguments))
        self.assertIn("--start-maximized", options.arguments)

    @patch("src.infrastructure.browser.webdriver.Chrome")
    def test_create_chrome_driver_uses_isolated_profile(self, chrome_driver):
        expected_driver = MagicMock()
        chrome_driver.return_value = expected_driver

        driver = self.factory.create_driver("chrome")

        self.assertIs(driver, expected_driver)
        options = chrome_driver.call_args.kwargs["options"]
        self.assertTrue(any(arg.startswith("user-data-dir=") for arg in options.arguments))
        self.assertIn("--disable-blink-features=AutomationControlled", options.arguments)

    @patch("src.infrastructure.browser.webdriver.Firefox")
    def test_create_firefox_driver_maximizes_window(self, firefox_driver):
        expected_driver = MagicMock()
        firefox_driver.return_value = expected_driver

        driver = self.factory.create_driver("firefox")

        self.assertIs(driver, expected_driver)
        expected_driver.maximize_window.assert_called_once()

    def test_unsupported_browser_raises_clear_error(self):
        with self.assertRaisesRegex(ValueError, "Navegador no soportado"):
            self.factory.create_driver("opera")


if __name__ == "__main__":
    unittest.main()
