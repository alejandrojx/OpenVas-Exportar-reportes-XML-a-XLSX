#!/usr/bin/env python3
"""
Asistente local para convertir reportes XML de Greenbone/OpenVAS a XLSX.

Este flujo no usa GMP/API. Esta pensado para GOS donde el reporte se exporta
desde la interfaz web como XML o Anonymous XML.
"""

from __future__ import annotations

import subprocess
import sys
from pathlib import Path


SCRIPT_DIR = Path(__file__).resolve().parent
PROJECT_DIR = SCRIPT_DIR.parent
EXPORTER = SCRIPT_DIR / "openvas_report_to_xlsx.py"
INPUT_DIR = PROJECT_DIR / "entradas"
OUTPUT_DIR = PROJECT_DIR / "salidas"


def ask(prompt: str, default: str = "", required: bool = True) -> str:
    while True:
        label = f"{prompt} [{default}]: " if default else f"{prompt}: "
        value = input(label).strip().strip('"')
        if not value and default:
            value = default
        if value or not required:
            return value
        print("Este dato es obligatorio.")


def list_xml_files(folder: Path) -> list[Path]:
    if not folder.exists():
        return []
    return sorted(folder.glob("*.xml"), key=lambda item: item.stat().st_mtime, reverse=True)


def choose_from_list(files: list[Path], title: str) -> Path | None:
    if not files:
        return None
    print("")
    print(title)
    print("-" * 90)
    for index, file in enumerate(files, start=1):
        size_kb = file.stat().st_size / 1024
        print(f"{index:>2}. {file.name:<55} {size_kb:>10.1f} KB")
    print("-" * 90)
    while True:
        value = ask("Numero del XML o Enter para cancelar", "", required=False)
        if not value:
            return None
        if value.isdigit() and 1 <= int(value) <= len(files):
            return files[int(value) - 1]
        print("Seleccion no valida.")


def choose_xml() -> Path:
    INPUT_DIR.mkdir(parents=True, exist_ok=True)
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

    while True:
        print("")
        print("Selecciona el reporte XML que esta en la carpeta entradas")
        selected = choose_from_list(list_xml_files(INPUT_DIR), f"XML en {INPUT_DIR}")
        if selected:
            return selected
        print("No se selecciono XML. Copia primero el reporte .xml a la carpeta entradas.")


def default_output_name(xml_path: Path) -> str:
    return f"{xml_path.stem}.xlsx"


def main() -> int:
    print("")
    print("Convertidor OpenVAS / Greenbone XML a XLSX")
    print("=" * 55)
    print("Exporta primero desde Greenbone como XML o Anonymous XML.")
    print("")

    if not EXPORTER.exists():
        print(f"No encuentro el convertidor base: {EXPORTER}")
        return 1

    xml_path = choose_xml()
    output_name = ask("Nombre del XLSX de salida (no necesitas escribir .xlsx)", default_output_name(xml_path))
    output_path = Path(output_name)
    if output_path.suffix.lower() != ".xlsx":
        output_path = output_path.with_suffix(".xlsx")
    if not output_path.is_absolute():
        output_path = OUTPUT_DIR / output_path.name

    print("")
    print(f"XML:  {xml_path}")
    print(f"XLSX: {output_path}")
    print("")

    completed = subprocess.run(
        [
            sys.executable,
            str(EXPORTER),
            "--xml",
            str(xml_path),
            "--output",
            str(output_path),
        ],
        check=False,
    )
    if completed.returncode != 0:
        print("")
        print("La conversion fallo. Verifica que el XML sea un reporte Greenbone/OpenVAS completo.")
        return completed.returncode

    print("")
    print(f"Listo: {output_path}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
