import tempfile
import unittest
from pathlib import Path
from unittest.mock import MagicMock, patch

from src.presentation.desktop.app_controller import AppController


class FakeEntry:
    def __init__(self):
        self.value = ""

    def delete(self, *_args, **_kwargs):
        self.value = ""

    def insert(self, _index, value):
        self.value = value


class FakeCombo:
    def __init__(self, value="Edge"):
        self.value = value

    def get(self):
        return self.value


class FakeConfigurable:
    def __init__(self):
        self.config = {}

    def configure(self, **kwargs):
        self.config.update(kwargs)


class FakeWindow:
    def __init__(self, base_dir):
        self.ruta_excel = None
        self.navegador_seleccionado = "Edge"
        self.entry_excel = FakeEntry()
        self.combo_navegador = FakeCombo("Edge")
        self.btn_iniciar = FakeConfigurable()
        self.label_info = FakeConfigurable()
        self.COLORES = {"amarillo": "#ff0", "gris_medio": "#999"}
        self.BASE_DIR = str(base_dir)
        self.LOGS_DIR = str(base_dir / "logs")
        self.enviando = False
        self.cancelar_envio = False
        self.logged_messages = []

    def agregar_log(self, mensaje):
        self.logged_messages.append(mensaje)

    def notificar_finalizacion(self):
        self.logged_messages.append("notificado")


class FakeThread:
    def __init__(self, target=None, daemon=None):
        self.target = target
        self.daemon = daemon
        self.started = False

    def start(self):
        self.started = True


class AppControllerTests(unittest.TestCase):
    def setUp(self):
        self.temp_dir = tempfile.TemporaryDirectory()
        self.base_dir = Path(self.temp_dir.name)
        self.window = FakeWindow(self.base_dir)
        self.browser_service = MagicMock()
        self.browser_service.ensure_profile.return_value = str(self.base_dir / "perfiles" / "edge")
        self.logger = MagicMock()

    def tearDown(self):
        self.temp_dir.cleanup()

    @patch("src.presentation.desktop.app_controller.filedialog.askopenfilename")
    def test_seleccionar_excel_actualiza_estado_visual(self, askopenfilename):
        archivo = self.base_dir / "contactos.xlsx"
        askopenfilename.return_value = str(archivo)
        controller = AppController(
            window=self.window,
            logger=self.logger,
            browser_service=self.browser_service,
            paths=MagicMock(),
        )

        controller.seleccionar_excel()

        self.assertEqual(self.window.ruta_excel, str(archivo))
        self.assertEqual(self.window.entry_excel.value, str(archivo))
        self.assertTrue(any("Archivo seleccionado" in msg for msg in self.window.logged_messages))

    @patch("src.presentation.desktop.app_controller.messagebox.showwarning")
    def test_iniciar_proceso_valida_excel_antes_de_lanzar_hilo(self, showwarning):
        controller = AppController(
            window=self.window,
            logger=self.logger,
            browser_service=self.browser_service,
            paths=MagicMock(),
        )

        controller.iniciar_proceso()

        showwarning.assert_called_once()

    @patch("src.presentation.desktop.app_controller.messagebox.askyesno", return_value=True)
    def test_iniciar_proceso_lanza_hilo_background(self, askyesno):
        archivo = self.base_dir / "contactos.xlsx"
        archivo.write_text("dummy", encoding="utf-8")
        self.window.ruta_excel = str(archivo)
        created_threads = []

        def thread_factory(target=None, daemon=None):
            thread = FakeThread(target=target, daemon=daemon)
            created_threads.append(thread)
            return thread

        controller = AppController(
            window=self.window,
            logger=self.logger,
            browser_service=self.browser_service,
            paths=MagicMock(),
            thread_factory=thread_factory,
        )

        controller.iniciar_proceso()

        askyesno.assert_called_once()
        self.assertEqual(len(created_threads), 1)
        self.assertTrue(created_threads[0].started)
        self.assertEqual(self.window.btn_iniciar.config["state"], "disabled")


if __name__ == "__main__":
    unittest.main()
