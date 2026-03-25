from __future__ import annotations

import os
import sys
from pathlib import Path


class AppPaths:
    """
    Resolver centralizado de rutas del proyecto y recursos de la app.
    """

    def __init__(self, anchor_file: str | Path | None = None):
        self._anchor_file = Path(anchor_file).resolve() if anchor_file else None

    @property
    def project_root(self) -> Path:
        if getattr(sys, "frozen", False):
            return Path(sys.executable).resolve().parent
        if self._anchor_file is not None:
            anchor = self._anchor_file
            if anchor.is_file():
                return anchor.parent
            return anchor
        return Path(__file__).resolve().parents[2]

    def get_base_dir(self) -> str:
        return str(self.project_root)

    def get_resource_path(self, nombre_archivo: str) -> str | None:
        posibles_rutas = []

        if getattr(sys, "frozen", False) and hasattr(sys, "_MEIPASS"):
            meipass = Path(sys._MEIPASS)
            posibles_rutas.extend([
                meipass / nombre_archivo,
                meipass / "src" / "resources" / nombre_archivo,
            ])

        base_dir = self.project_root
        posibles_rutas.extend([
            base_dir / nombre_archivo,
            base_dir / "src" / "resources" / nombre_archivo,
            Path.cwd() / nombre_archivo,
            Path.cwd() / "src" / "resources" / nombre_archivo,
        ])

        for ruta in posibles_rutas:
            if ruta.exists():
                return str(ruta)
        return None

    def ensure_dir(self, *parts: str) -> str:
        ruta = self.project_root.joinpath(*parts)
        ruta.mkdir(parents=True, exist_ok=True)
        return str(ruta)

    def get_logs_dir(self) -> str:
        return self.ensure_dir("logs")

    def get_profile_dir(self, navegador: str) -> str:
        return self.ensure_dir("perfiles", navegador.lower())


def obtener_ruta_base(anchor_file: str | Path | None = None) -> str:
    return AppPaths(anchor_file=anchor_file).get_base_dir()


def obtener_ruta_recurso(nombre_archivo: str, anchor_file: str | Path | None = None) -> str | None:
    return AppPaths(anchor_file=anchor_file).get_resource_path(nombre_archivo)


def obtener_ruta_perfiles(navegador: str, anchor_file: str | Path | None = None) -> str:
    return AppPaths(anchor_file=anchor_file).get_profile_dir(navegador)
