"""
Build script for Blitz WaSender using PyInstaller --onedir.
Usage: .\\.venv\\Scripts\\python.exe build_executable.py
"""

from __future__ import annotations

import shutil
import sys
from pathlib import Path

import PyInstaller.__main__


APP_NAME = "BlitzWaSender"
ENTRYPOINT = "gui_app.py"

PROJECT_ROOT = Path(__file__).resolve().parent
PACKAGE_DIR = PROJECT_ROOT / "src"
RESOURCES_DIR = PROJECT_ROOT / "src" / "resources"
ICON_PATH = RESOURCES_DIR / "app_icon.ico"
THEMES_PATH = RESOURCES_DIR / "themes.json"

DIST_DIR = PROJECT_ROOT / "dist"
BUILD_DIR = PROJECT_ROOT / "build"
SPEC_DIR = PROJECT_ROOT / "spec"
SPEC_FILE = SPEC_DIR / f"{APP_NAME}.spec"


REQUIRED_PATHS = [
    ("Entrypoint", PROJECT_ROOT / ENTRYPOINT),
    ("Package", PACKAGE_DIR),
    ("Resources directory", RESOURCES_DIR),
    ("App icon", ICON_PATH),
    ("Themes file", THEMES_PATH),
]


PYINSTALLER_ARGS = [
    ENTRYPOINT,
    f"--name={APP_NAME}",
    "--onedir",
    "--windowed",
    f"--specpath={SPEC_DIR}",
    f"--paths={PROJECT_ROOT}",
    f"--add-data={RESOURCES_DIR};src/resources",
    "--clean",
    "--noconfirm",
    "--noupx",
    "--optimize=1",
    "--collect-data=customtkinter",
    "--collect-submodules=customtkinter",
    "--collect-submodules=darkdetect",
    "--collect-submodules=pandas",
    "--collect-submodules=openpyxl",
    "--collect-submodules=numpy",
    "--collect-submodules=selenium",
    "--hidden-import=tkinter",
    "--hidden-import=tkinter.filedialog",
    "--hidden-import=tkinter.messagebox",
    "--hidden-import=psutil",
]


def is_venv() -> bool:
    return (
        hasattr(sys, "real_prefix")
        or (hasattr(sys, "base_prefix") and sys.base_prefix != sys.prefix)
        or sys.prefix != getattr(sys, "base_prefix", sys.prefix)
    )


def confirm_execution() -> bool:
    print("\n" + "=" * 70)
    print("BUILD CONFIRMATION")
    print("=" * 70)
    print("\nThis script will compile Blitz WaSender with PyInstaller.")
    print("\nActions:")
    print("  - Clean folders: dist/, build/, spec/")
    print("  - Bundle gui_app.py in onedir mode")
    print("  - Include package src and src/resources/")
    print(f"  - Generate executable in: {DIST_DIR / APP_NAME}")
    print("\n" + "=" * 70)

    while True:
        response = input("\nProceed? (y/n): ").strip().lower()
        if response in {"y", "yes"}:
            return True
        if response in {"n", "no"}:
            print("\nBuild cancelled by user.")
            return False
        print("Invalid response. Enter 'y' or 'n'.")


def analyze_paths() -> bool:
    print("\n" + "=" * 70)
    print("PRE-BUILD DIAGNOSTICS")
    print("=" * 70)

    ok = True
    for label, path in REQUIRED_PATHS:
        if path.exists():
            print(f"  OK  {label}: {path.relative_to(PROJECT_ROOT)}")
        else:
            print(f"  MISSING  {label}: {path.relative_to(PROJECT_ROOT)}")
            ok = False

    print("\nBundle layout analysis:")
    print(f"  Project root: {PROJECT_ROOT}")
    print(f"  Entrypoint: {PROJECT_ROOT / ENTRYPOINT}")
    print(f"  Package root: {PACKAGE_DIR}")
    print(f"  Add-data mapping: {RESOURCES_DIR} -> src/resources")
    print(f"  Expected bundled resources: dist/{APP_NAME}/_internal/src/resources")
    print("  Expected runtime resource lookup: _MEIPASS/src/resources/<file>")
    print("  Logs and perfiles will be created at runtime next to the executable.")

    return ok


def clean_previous_builds() -> None:
    if DIST_DIR.exists():
        shutil.rmtree(DIST_DIR)
        print("Previous dist/ removed")
    if BUILD_DIR.exists():
        shutil.rmtree(BUILD_DIR)
        print("Previous build/ removed")
    if SPEC_FILE.exists():
        SPEC_FILE.unlink()
        print("Previous spec file removed")


def build_exe() -> bool:
    if not analyze_paths():
        print("\nDiagnostics failed. Fix missing paths before building.")
        return False

    SPEC_DIR.mkdir(exist_ok=True)
    clean_previous_builds()

    print("\n" + "=" * 70)
    print(f"COMPILING {APP_NAME} WITH PYINSTALLER")
    print("=" * 70 + "\n")

    pyinstaller_args = list(PYINSTALLER_ARGS)
    if ICON_PATH.exists():
        pyinstaller_args.append(f"--icon={ICON_PATH}")
    else:
        print("WARNING: Icon not found. Continuing without --icon.")

    PyInstaller.__main__.run(pyinstaller_args)

    print("\n" + "=" * 70)
    print("BUILD COMPLETED")
    print("=" * 70)
    print(f"Bundle location: {DIST_DIR / APP_NAME}")

    exe_path = DIST_DIR / APP_NAME / f"{APP_NAME}.exe"
    bundled_themes = DIST_DIR / APP_NAME / "_internal" / "src" / "resources" / "themes.json"
    bundled_icon = DIST_DIR / APP_NAME / "_internal" / "src" / "resources" / "app_icon.ico"

    checks = [
        ("Executable", exe_path),
        ("Bundled themes", bundled_themes),
        ("Bundled icon", bundled_icon),
    ]

    all_ok = True
    for label, path in checks:
        if path.exists():
            print(f"Verification OK: {path}")
        else:
            print(f"Verification FAILED ({label}): {path}")
            all_ok = False

    if exe_path.exists():
        size_mb = exe_path.stat().st_size / (1024 * 1024)
        print(f"Executable size: {size_mb:.2f} MB")

    return all_ok


if __name__ == "__main__":
    print("\n" + "=" * 70)
    print(f"{APP_NAME} - EXECUTABLE GENERATOR")
    print("=" * 70)

    if not is_venv():
        print("\nERROR: No virtual environment detected.")
        print("This script must run inside the project virtual environment.")
        print("Activate with: .venv\\Scripts\\activate")
        sys.exit(1)

    print("\nVirtual environment detected")
    print(f"  Python: {sys.version.split()[0]}")
    print(f"  Location: {sys.prefix}")

    if not confirm_execution():
        sys.exit(0)

    try:
        success = build_exe()
        if success:
            print("\nBuild completed successfully.")
            print("Next steps:")
            print(f"  1. Test the executable in: {DIST_DIR / APP_NAME}")
            print(f"  2. Verify logs/gui_app.log is created on first launch")
            print(f"  3. Compress the folder into a ZIP for distribution")
        else:
            print("\nBuild completed with verification errors.")
            sys.exit(1)
    except Exception as exc:
        print(f"\nBuild error: {exc}")
        import traceback

        traceback.print_exc()
        sys.exit(1)
