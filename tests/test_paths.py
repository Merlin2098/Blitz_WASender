import tempfile
import unittest
from pathlib import Path

from src.infrastructure.paths import AppPaths


class AppPathsTests(unittest.TestCase):
    def test_anchor_file_defines_project_root_and_managed_dirs(self):
        with tempfile.TemporaryDirectory() as tmpdir:
            root = Path(tmpdir)
            anchor = root / "gui_app.py"
            anchor.write_text("# anchor\n", encoding="utf-8")

            paths = AppPaths(anchor_file=anchor)

            self.assertEqual(paths.project_root, root)
            self.assertEqual(paths.get_base_dir(), str(root))

            logs_dir = Path(paths.get_logs_dir())
            profile_dir = Path(paths.get_profile_dir("Edge"))

            self.assertTrue(logs_dir.exists())
            self.assertEqual(logs_dir, root / "logs")
            self.assertTrue(profile_dir.exists())
            self.assertEqual(profile_dir, root / "perfiles" / "edge")

    def test_resource_lookup_prefers_project_resource_folder(self):
        with tempfile.TemporaryDirectory() as tmpdir:
            root = Path(tmpdir)
            anchor = root / "gui_app.py"
            resource_dir = root / "src" / "resources"
            resource_dir.mkdir(parents=True)
            anchor.write_text("# anchor\n", encoding="utf-8")

            icon = resource_dir / "app_icon.ico"
            icon.write_text("icon", encoding="utf-8")

            paths = AppPaths(anchor_file=anchor)

            self.assertEqual(paths.get_resource_path("app_icon.ico"), str(icon))


if __name__ == "__main__":
    unittest.main()
