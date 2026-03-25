import tempfile
import unittest
from pathlib import Path

from src.infrastructure.session_logging import close_session_logger, create_session_logger


class SessionLoggingTests(unittest.TestCase):
    def test_create_session_logger_uses_fixed_filename(self):
        with tempfile.TemporaryDirectory() as tmpdir:
            context = create_session_logger("gui_app", tmpdir, filename="gui_app.log", overwrite=True)
            try:
                self.assertEqual(context.session_scope, "app_launch")
                self.assertEqual(Path(context.log_path).name, "gui_app.log")
                self.assertTrue(Path(context.log_path).exists())
            finally:
                close_session_logger(context.logger)

    def test_create_session_logger_overwrites_previous_content(self):
        with tempfile.TemporaryDirectory() as tmpdir:
            log_path = Path(tmpdir) / "gui_app.log"
            log_path.write_text("contenido_anterior", encoding="utf-8")

            context = create_session_logger("gui_app", tmpdir, filename="gui_app.log", overwrite=True)
            try:
                context.logger.info("mensaje nuevo")
            finally:
                close_session_logger(context.logger)

            contenido = log_path.read_text(encoding="utf-8")
            self.assertIn("mensaje nuevo", contenido)
            self.assertNotIn("contenido_anterior", contenido)


if __name__ == "__main__":
    unittest.main()
