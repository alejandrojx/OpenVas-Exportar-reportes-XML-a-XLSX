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


def prompt_header(title: str, subtitle: str = "") -> None:
    print("")
    print("=" * 79)
    print(title)
    print("-" * 79)
    if subtitle:
        print(subtitle)
        print("")


def ask_value(title: str, default: str = "", note: str = "", required: bool = True) -> str:
    prompt_header(title)
    if default:
        print(f"Default: {default}")
    if note:
        print(f"Note: {note}")
    print("")
    while True:
        value = input("ENTER VALUE, OR PRESS <ENTER> TO ACCEPT THE DEFAULT:: ").strip().strip('"')
        if not value and default:
            value = default
        if value or not required:
            return value
        print("A value is required.")


def ask_menu(title: str, options: list[str], default_index: int = 1, subtitle: str = "") -> int | None:
    if not options:
        return None
    while True:
        prompt_header(title, subtitle)
        for index, option in enumerate(options, start=1):
            marker = "->" if index == default_index else "  "
            print(f"  {marker}{index}- {option}")
        print("")
        value = input("ENTER THE NUMBER FOR YOUR CHOICE, OR PRESS <ENTER> TO ACCEPT THE DEFAULT:: ").strip()
        if not value:
            return default_index
        if value.isdigit() and 1 <= int(value) <= len(options):
            return int(value)
        print("")
        print("Invalid selection. Try again.")


def list_xml_files(folder: Path) -> list[Path]:
    if not folder.exists():
        return []
    return sorted(folder.glob("*.xml"), key=lambda item: item.stat().st_mtime, reverse=True)


def choose_from_list(files: list[Path], title: str) -> Path | None:
    if not files:
        return None
    options = []
    for file in files:
        size_kb = file.stat().st_size / 1024
        options.append(f"{file.name} ({size_kb:.1f} KB)")
    selected = ask_menu(title, options, default_index=1, subtitle=str(INPUT_DIR))
    if selected is None:
        return None
    return files[selected - 1]


def choose_xml() -> Path:
    INPUT_DIR.mkdir(parents=True, exist_ok=True)
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

    while True:
        selected = choose_from_list(
            list_xml_files(INPUT_DIR),
            "Select the OpenVAS XML report to convert",
        )
        if selected:
            return selected
        prompt_header("No XML reports found")
        print(f"Copy the exported .xml report to: {INPUT_DIR}")
        input("Press <ENTER> to try again...")


def default_output_name(xml_path: Path) -> str:
    return f"{xml_path.stem}.xlsx"


def main() -> int:
    prompt_header(
        "OpenVAS / Greenbone XML to XLSX Converter",
        "Export the report from Greenbone Web as XML or Anonymous XML before running this tool.",
    )

    if not EXPORTER.exists():
        print(f"No encuentro el convertidor base: {EXPORTER}")
        return 1

    xml_path = choose_xml()
    output_name = ask_value(
        "Enter the XLSX output name",
        default_output_name(xml_path),
        "You do not need to type the .xlsx extension.",
    )
    output_path = Path(output_name)
    if output_path.suffix.lower() != ".xlsx":
        output_path = output_path.with_suffix(".xlsx")
    if not output_path.is_absolute():
        output_path = OUTPUT_DIR / output_path.name

    prompt_header("Converting report")
    print(f"XML : {xml_path}")
    print(f"XLSX: {output_path}")
    print("")
    sys.stdout.flush()

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

    prompt_header("Conversion completed")
    print(f"Output: {output_path}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
