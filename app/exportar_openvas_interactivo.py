#!/usr/bin/env python3
"""
Asistente interactivo para exportar reportes Greenbone/OpenVAS a XLSX.

Ejecuta este archivo y responde las preguntas. El script llamara a
openvas_report_to_xlsx.py con los datos ingresados.
"""

from __future__ import annotations

import getpass
import socket
import shutil
import subprocess
import sys
import xml.etree.ElementTree as ET
from pathlib import Path


SCRIPT_DIR = Path(__file__).resolve().parent
PROJECT_DIR = SCRIPT_DIR.parent
EXPORTER = SCRIPT_DIR / "openvas_report_to_xlsx.py"
DEFAULT_OUTPUT_DIR = PROJECT_DIR / "salidas"
LOCAL_GVM_CLI = PROJECT_DIR / ".venv" / "Scripts" / "gvm-cli.exe"


def ask(prompt: str, default: str = "", required: bool = True) -> str:
    while True:
        label = f"{prompt} [{default}]: " if default else f"{prompt}: "
        value = input(label).strip()
        if not value and default:
            value = default
        if value or not required:
            return value
        print("Este dato es obligatorio.")


def ask_password() -> str:
    while True:
        password = getpass.getpass("Password GMP: ")
        if password:
            return password
        print("El password es obligatorio.")


def tcp_check(host: str, port: str, timeout: float = 5.0) -> tuple[bool, str]:
    try:
        with socket.create_connection((host, int(port)), timeout=timeout):
            return True, "OK"
    except ValueError:
        return False, "Puerto no numerico"
    except TimeoutError:
        return False, "Timeout"
    except OSError as error:
        return False, str(error)


def normalize_output(value: str) -> Path:
    output = Path(value)
    if output.suffix.lower() != ".xlsx":
        output = output.with_suffix(".xlsx")
    if not output.is_absolute():
        if output.parent == Path("."):
            output = DEFAULT_OUTPUT_DIR / output
        else:
            output = PROJECT_DIR / output
    return output


def print_header() -> None:
    print("")
    print("Exportador interactivo OpenVAS / Greenbone a XLSX")
    print("=" * 55)
    print("El asistente buscara gvm-cli automaticamente.")
    print("En Greenbone normalmente GMP usa TLS por el puerto 9390.")
    print("")


def find_gvm_cli() -> str:
    if LOCAL_GVM_CLI.exists():
        return str(LOCAL_GVM_CLI)
    found = shutil.which("gvm-cli")
    if found:
        return found
    return "gvm-cli"


def run_gmp_xml(
    gvm_cli: str,
    host: str,
    port: str,
    username: str,
    password: str,
    xml_request: str,
) -> subprocess.CompletedProcess:
    return subprocess.run(
        [
            gvm_cli,
            "--gmp-username",
            username,
            "--gmp-password",
            password,
            "tls",
            "--hostname",
            host,
            "--port",
            port,
            "--xml",
            xml_request,
        ],
        check=False,
        capture_output=True,
    )


def clean_text(value: str | None) -> str:
    return (value or "").replace("\n", " ").strip()


def node_text(parent: ET.Element, path: str) -> str:
    node = parent.find(path)
    return clean_text(node.text if node is not None else "")


def list_reports(
    gvm_cli: str,
    host: str,
    port: str,
    username: str,
    password: str,
    rows: int = 20,
) -> list[dict[str, str]]:
    request = f'<get_reports filter="rows={rows} sort-reverse=date" details="0"/>'
    completed = run_gmp_xml(gvm_cli, host, port, username, password, request)
    if completed.returncode != 0:
        stderr = completed.stderr.decode("utf-8", errors="replace").strip()
        stdout = completed.stdout.decode("utf-8", errors="replace").strip()
        print("")
        print("No pude listar reportes por GMP.")
        if stderr:
            print(stderr)
        elif stdout:
            print(stdout)
        return []

    try:
        root = ET.fromstring(completed.stdout)
    except ET.ParseError as error:
        print("")
        print(f"La respuesta de GMP no parece XML valido: {error}")
        return []

    reports: list[dict[str, str]] = []
    for report in root.findall(".//report"):
        report_id = report.get("id", "")
        if not report_id:
            continue
        task_name = node_text(report, "./task/name")
        scan_start = node_text(report, "scan_start")
        scan_end = node_text(report, "scan_end")
        severity = node_text(report, "severity/full") or node_text(report, "severity")
        reports.append(
            {
                "id": report_id,
                "task": task_name or "(sin nombre)",
                "start": scan_start or "-",
                "end": scan_end or "-",
                "severity": severity or "-",
            }
        )
    return reports


def choose_report_id(
    gvm_cli: str,
    host: str,
    port: str,
    username: str,
    password: str,
) -> str:
    print("")
    show_list = ask("Listar reportes disponibles ahora? S/N", "S").lower()
    if show_list not in {"s", "si", "sí", "y", "yes"}:
        return ask("UUID del reporte")

    reports = list_reports(gvm_cli, host, port, username, password)
    if not reports:
        return ask("UUID del reporte")

    print("")
    print("Reportes encontrados:")
    print("-" * 100)
    for index, report in enumerate(reports, start=1):
        print(
            f"{index:>2}. {report['task'][:38]:<38} "
            f"Inicio: {report['start'][:19]:<19} "
            f"Sev: {report['severity']:<6} "
            f"ID: {report['id']}"
        )
    print("-" * 100)

    while True:
        value = ask("Numero del reporte o UUID manual")
        if value.isdigit():
            index = int(value)
            if 1 <= index <= len(reports):
                selected = reports[index - 1]
                print(f"Seleccionado: {selected['task']} ({selected['id']})")
                return selected["id"]
        if len(value) >= 32:
            return value
        print("Seleccion no valida.")


def main() -> int:
    print_header()

    if not EXPORTER.exists():
        print(f"No encuentro el exportador base: {EXPORTER}")
        return 1

    gvm_cli = find_gvm_cli()
    print(f"gvm-cli: {gvm_cli}")
    host = ask("IP o FQDN de Greenbone/OpenVAS")
    port = ask("Puerto GMP", "9390")
    print("")
    print(f"Probando conectividad TCP a {host}:{port}...")
    tcp_ok, tcp_message = tcp_check(host, port)
    if tcp_ok:
        print("Puerto accesible.")
    else:
        print(f"No se pudo conectar a {host}:{port}: {tcp_message}")
        print("")
        print("Esto normalmente significa que GMP no esta expuesto desde tu equipo.")
        print("La web de Greenbone puede funcionar por 443 aunque GMP/API no este abierto.")
        print("Valida en el appliance/firewall que el servicio GMP escuche por 9390 o el puerto correcto.")
        continue_anyway = ask("Continuar de todos modos? S/N", "N").lower()
        if continue_anyway not in {"s", "si", "sí", "y", "yes"}:
            return 1

    username = ask("Usuario GMP")
    password = ask_password()
    report_id = choose_report_id(gvm_cli, host, port, username, password)
    min_qod = ask("Min QoD", "70")
    levels = ask("Niveles a exportar, por ejemplo hml o chml", "hml")
    output = normalize_output(ask("Archivo XLSX de salida", "reporte_openvas.xlsx"))

    report_filter = (
        f"apply_overrides=0 levels={levels} rows=0 min_qod={min_qod} "
        "first=1 sort-reverse=severity"
    )

    command = [
        sys.executable,
        str(EXPORTER),
        "--gmp-host",
        host,
        "--gmp-port",
        port,
        "--username",
        username,
        "--password",
        password,
        "--report-id",
        report_id,
        "--filter",
        report_filter,
        "--gvm-cli",
        gvm_cli,
        "--output",
        str(output),
    ]

    print("")
    print("Descargando reporte y generando XLSX...")
    print("")

    try:
        completed = subprocess.run(command, check=False)
    except FileNotFoundError:
        print("No se pudo ejecutar Python o gvm-cli. Revisa la ruta ingresada.")
        return 1

    if completed.returncode != 0:
        print("")
        print("La exportacion fallo.")
        print("Revisa IP, puerto, credenciales, UUID del reporte y acceso TLS/GMP.")
        return completed.returncode

    print("")
    print(f"Listo: {output}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
