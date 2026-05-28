#!/usr/bin/env python3
"""Genera la guia PDF del convertidor OpenVAS."""

from __future__ import annotations

from pathlib import Path

from reportlab.lib import colors
from reportlab.lib.enums import TA_CENTER
from reportlab.lib.pagesizes import letter
from reportlab.lib.styles import ParagraphStyle, getSampleStyleSheet
from reportlab.lib.units import inch
from reportlab.platypus import ListFlowable, ListItem, Paragraph, SimpleDocTemplate, Spacer
from reportlab.platypus import Table, TableStyle


PROJECT_DIR = Path(__file__).resolve().parent.parent
PDF_PATH = PROJECT_DIR / "Instrucciones_Convertidor_OpenVAS.pdf"


def p(text: str, style: ParagraphStyle) -> Paragraph:
    return Paragraph(text, style)


def bullets(items: list[str], style: ParagraphStyle) -> ListFlowable:
    return ListFlowable(
        [ListItem(p(item, style), leftIndent=12) for item in items],
        bulletType="bullet",
        leftIndent=18,
    )


def main() -> int:
    doc = SimpleDocTemplate(
        str(PDF_PATH),
        pagesize=letter,
        rightMargin=0.65 * inch,
        leftMargin=0.65 * inch,
        topMargin=0.6 * inch,
        bottomMargin=0.6 * inch,
        title="Instrucciones Convertidor OpenVAS",
    )
    styles = getSampleStyleSheet()
    title = ParagraphStyle(
        "TitleCustom",
        parent=styles["Title"],
        fontName="Helvetica-Bold",
        fontSize=18,
        leading=22,
        alignment=TA_CENTER,
        textColor=colors.HexColor("#1F4E79"),
        spaceAfter=14,
    )
    h1 = ParagraphStyle(
        "HeadingCustom",
        parent=styles["Heading1"],
        fontSize=13,
        leading=16,
        textColor=colors.HexColor("#1F4E79"),
        spaceBefore=8,
        spaceAfter=6,
    )
    body = ParagraphStyle("BodyCustom", parent=styles["BodyText"], fontSize=9.5, leading=13)
    code = ParagraphStyle(
        "CodeCustom",
        parent=styles["BodyText"],
        fontName="Courier",
        fontSize=8,
        leading=11,
        backColor=colors.HexColor("#F3F6FA"),
        borderColor=colors.HexColor("#D9E2F3"),
        borderWidth=0.5,
        borderPadding=5,
        spaceBefore=4,
        spaceAfter=6,
    )

    table = Table(
        [
            ["Carpeta", "Uso"],
            ["entradas", "Aqui se dejan los reportes XML exportados desde OpenVAS/Greenbone."],
            ["salidas", "Aqui se generan automaticamente los archivos XLSX y PDF."],
            ["app/config", "Archivos internos del convertidor. No se modifican para uso normal."],
        ],
        colWidths=[1.35 * inch, 5.55 * inch],
        repeatRows=1,
    )
    table.setStyle(TableStyle([
        ("BACKGROUND", (0, 0), (-1, 0), colors.HexColor("#1F4E79")),
        ("TEXTCOLOR", (0, 0), (-1, 0), colors.white),
        ("FONTNAME", (0, 0), (-1, 0), "Helvetica-Bold"),
        ("FONTSIZE", (0, 0), (-1, -1), 8.5),
        ("GRID", (0, 0), (-1, -1), 0.25, colors.HexColor("#D9E2F3")),
        ("ROWBACKGROUNDS", (0, 1), (-1, -1), [colors.white, colors.HexColor("#F3F6FA")]),
        ("VALIGN", (0, 0), (-1, -1), "TOP"),
        ("LEFTPADDING", (0, 0), (-1, -1), 5),
        ("RIGHTPADDING", (0, 0), (-1, -1), 5),
        ("TOPPADDING", (0, 0), (-1, -1), 5),
        ("BOTTOMPADDING", (0, 0), (-1, -1), 5),
    ]))

    story = [
        p("Guia de uso - Convertidor OpenVAS XML a XLSX y PDF", title),
        p("Este convertidor toma un reporte XML exportado desde Greenbone/OpenVAS y genera dos archivos: un XLSX tecnico con varias hojas de analisis y un PDF ejecutivo resumido.", body),
        Spacer(1, 0.1 * inch),
        p("1. Exportar el XML desde Greenbone", h1),
        bullets([
            "Abra el reporte en la interfaz web de Greenbone/OpenVAS.",
            "Use la opcion de exportacion y seleccione XML o Anonymous XML.",
            "Guarde el archivo XML en su equipo.",
        ], body),
        p("2. Copiar el XML a la carpeta de entrada", h1),
        p("Pegue el archivo XML dentro de la carpeta:", body),
        p(str(PROJECT_DIR / "entradas"), code),
        p("Si las carpetas internas estan ocultas, puede pegar esa ruta directamente en la barra de direcciones del Explorador de Windows.", body),
        p("3. Ejecutar el convertidor", h1),
        p("En la raiz de la carpeta ejecute:", body),
        p("convertir_xml_a_xlsx.bat", code),
        p("El menu mostrara los XML encontrados en entradas. Puede escribir el numero de la opcion o presionar Enter para aceptar la opcion predeterminada.", body),
        p("4. Nombre del archivo de salida", h1),
        bullets([
            "Cuando pregunte por el nombre del XLSX, escriba solo el nombre base si lo desea.",
            "No es necesario escribir la extension .xlsx.",
            "El PDF se creara con el mismo nombre base y extension .pdf.",
        ], body),
        p("Ejemplo:", body),
        p("Nombre ingresado: informe_switch_core<br/>Salida XLSX: salidas\\informe_switch_core.xlsx<br/>Salida PDF: salidas\\informe_switch_core.pdf", code),
        p("5. Resultado", h1),
        p("Los archivos convertidos quedan en:", body),
        p(str(PROJECT_DIR / "salidas"), code),
        table,
        p("Notas importantes", h1),
        bullets([
            "Si el XML no trae hostname, el convertidor intenta resolverlo desde el PC usando DNS reverso.",
            "Para que el hostname aparezca, el DNS debe tener registro PTR para la IP.",
            "El XLSX incluye hojas de resumen, vulnerabilidades, hosts, CVEs y remediacion.",
            "El PDF es un resumen ejecutivo rapido para compartir o revisar sin abrir Excel.",
        ], body),
    ]

    doc.build(story)
    print(PDF_PATH)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
