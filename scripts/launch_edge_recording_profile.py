from __future__ import annotations

import argparse
import json
import os
import shutil
import subprocess
from datetime import datetime
from pathlib import Path


PROJECT_ROOT = Path(__file__).resolve().parents[1]


COMMON_EDGE_PATHS = [
    Path(r"C:\Program Files (x86)\Microsoft\Edge\Application\msedge.exe"),
    Path(r"C:\Program Files\Microsoft\Edge\Application\msedge.exe"),
]


def timestamp_slug() -> str:
    return datetime.now().strftime("%Y%m%d_%H%M%S")


def default_profile_dir() -> Path:
    return PROJECT_ROOT / "perfiles" / "edge"


def resolve_edge_path(custom_path: str | None) -> Path:
    candidates: list[Path] = []

    if custom_path:
        candidates.append(Path(custom_path))

    env_path = os.environ.get("EDGE_PATH")
    if env_path:
        candidates.append(Path(env_path))

    which_path = shutil.which("msedge")
    if which_path:
        candidates.append(Path(which_path))

    candidates.extend(COMMON_EDGE_PATHS)

    for candidate in candidates:
        if candidate and candidate.exists():
            return candidate

    raise FileNotFoundError(
        "No se encontró msedge.exe. Usa --edge-path o define EDGE_PATH."
    )


def build_launch_log_dir() -> Path:
    output_dir = PROJECT_ROOT / "logs" / "recording_launches" / timestamp_slug()
    output_dir.mkdir(parents=True, exist_ok=True)
    return output_dir


def build_command(edge_path: Path, profile_dir: Path, args: argparse.Namespace) -> list[str]:
    command = [
        str(edge_path),
        f"--user-data-dir={profile_dir}",
        "--no-first-run",
        "--no-default-browser-check",
    ]

    if args.new_window:
        command.append("--new-window")

    if args.remote_debugging_port:
        command.append(f"--remote-debugging-port={args.remote_debugging_port}")

    if args.start_maximized:
        command.append("--start-maximized")

    urls = list(args.url or [])
    if not urls:
        urls = ["https://web.whatsapp.com"]

    command.extend(urls)
    return command


def write_json(path: Path, payload: dict) -> None:
    path.write_text(json.dumps(payload, indent=2, ensure_ascii=False), encoding="utf-8")


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Lanza Microsoft Edge con el perfil aislado usado por Selenium."
    )
    parser.add_argument("--edge-path", help="Ruta opcional a msedge.exe.")
    parser.add_argument("--profile-dir", help="Ruta opcional al perfil de Edge.")
    parser.add_argument(
        "--url",
        action="append",
        help="URL a abrir. Puedes repetir --url varias veces. Por defecto abre WhatsApp Web.",
    )
    parser.add_argument(
        "--remote-debugging-port",
        type=int,
        default=9222,
        help="Puerto opcional para depuración remota de Chromium.",
    )
    parser.add_argument(
        "--new-window",
        action="store_true",
        help="Abre Edge en una ventana nueva.",
    )
    parser.add_argument(
        "--start-maximized",
        action="store_true",
        help="Inicia la ventana maximizada.",
    )
    args = parser.parse_args()

    edge_path = resolve_edge_path(args.edge_path)
    profile_dir = Path(args.profile_dir).resolve() if args.profile_dir else default_profile_dir()
    profile_dir.mkdir(parents=True, exist_ok=True)
    log_dir = build_launch_log_dir()

    command = build_command(edge_path, profile_dir, args)
    process = subprocess.Popen(command)

    manifest = {
        "started_at": datetime.now().isoformat(),
        "edge_path": str(edge_path),
        "profile_dir": str(profile_dir),
        "pid": process.pid,
        "command": command,
        "remote_debugging_port": args.remote_debugging_port,
        "notes": [
            "Este launcher abre el mismo perfil aislado que usa la app con Selenium.",
            "Instala o habilita Selenium IDE dentro de este perfil si quieres grabar acciones.",
            "Realiza manualmente la secuencia en WhatsApp Web y exporta el flujo grabado cuando termines.",
        ],
    }
    write_json(log_dir / "launch_manifest.json", manifest)

    print("Edge lanzado para grabación.")
    print(f"PID: {process.pid}")
    print(f"Edge: {edge_path}")
    print(f"Perfil: {profile_dir}")
    print(f"Manifest: {log_dir / 'launch_manifest.json'}")
    print()
    print("Siguiente paso sugerido:")
    print("1. En esa ventana instala o abre Selenium IDE en ese mismo perfil.")
    print("2. Graba la secuencia manual en WhatsApp Web.")
    print("3. Exporta el flujo grabado y compárteme los pasos o el código exportado.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
