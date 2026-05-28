#!/usr/bin/env python3
"""
Prepara una instalacion local para el exportador.

Crea .venv dentro de Exportar_Informe e instala:
- gvm-tools, que provee gvm-cli
- openpyxl, usado para generar XLSX
- reportlab, usado para generar PDF ejecutivo
"""

from __future__ import annotations

import subprocess
import sys
import venv
from pathlib import Path


SCRIPT_DIR = Path(__file__).resolve().parent
PROJECT_DIR = SCRIPT_DIR.parent
VENV_DIR = PROJECT_DIR / ".venv"
VENV_PYTHON = VENV_DIR / "Scripts" / "python.exe"
GVM_CLI = VENV_DIR / "Scripts" / "gvm-cli.exe"
REQUIRED_PACKAGES = ["gvm-tools", "openpyxl", "reportlab"]


def run_quiet(command: list[str]) -> None:
    completed = subprocess.run(command, check=False, capture_output=True, text=True)
    if completed.returncode == 0:
        return

    print("")
    print("La instalacion fallo. Detalle:")
    if completed.stdout.strip():
        print(completed.stdout.strip())
    if completed.stderr.strip():
        print(completed.stderr.strip())
    raise SystemExit(completed.returncode)


def main() -> int:
    print("")
    print("Preparando dependencias locales de Exportar_Informe")
    print("=" * 55)

    if not VENV_PYTHON.exists():
        print(f"Creando entorno local: {VENV_DIR}")
        venv.EnvBuilder(with_pip=True, clear=False).create(VENV_DIR)

    print("Instalando/validando dependencias locales. Esto puede tardar unos minutos...")
    run_quiet([
        str(VENV_PYTHON),
        "-m",
        "pip",
        "install",
        "--disable-pip-version-check",
        "--upgrade",
        "pip",
        *REQUIRED_PACKAGES,
    ])

    if GVM_CLI.exists():
        print(f"gvm-cli disponible en: {GVM_CLI}")

    print("")
    print("Dependencias listas.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
