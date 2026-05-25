# OpenVAS / Greenbone - Convertir reportes XML a XLSX

Herramienta para convertir reportes exportados desde Greenbone/OpenVAS en formato `XML` o `Anonymous XML` a un archivo Excel `.xlsx` con hojas organizadas para analisis tecnico y remediacion.

## Uso rapido

1. Exporta el reporte desde Greenbone Web como `XML` o `Anonymous XML`.
2. Copia el archivo `.xml` a la carpeta `entradas`.
3. Ejecuta:

```powershell
.\convertir_xml_a_xlsx.bat
```

4. Selecciona el numero del XML.
5. Escribe el nombre del XLSX de salida.

No necesitas escribir la extension `.xlsx`; el asistente la agrega automaticamente.

Los archivos generados quedan en:

```text
salidas
```

## Estructura

```text
Convertir_Informe_Openvas/
  convertir_xml_a_xlsx.bat
  Instrucciones_Convertidor_OpenVAS.docx
  app/
    convertir_xml_interactivo.py
    openvas_report_to_xlsx.py
  entradas/
  salidas/
  ejemplos/
  config/
```

## Hojas del Excel

El XLSX generado incluye:

- `Indice`: enlaces internos a las hojas del reporte.
- `Resumen`: datos generales, conteos y grafico por severidad.
- `Vulnerabilidades`: hallazgos tecnicos completos.
- `Por_Host`: vista operativa por activo.
- `Hosts`: consolidado por host afectado.
- `Vuln_Detalle`: vulnerabilidades deduplicadas con hosts, impacto y solucion.
- `CVEs`: agrupacion por CVE.
- `Remediacion`: lista priorizada de remediacion.

## Uso manual

Tambien puedes ejecutar el convertidor directamente:

```powershell
.\.venv\Scripts\python.exe .\app\openvas_report_to_xlsx.py `
  --xml .\entradas\reporte.xml `
  --output .\salidas\reporte.xlsx
```

Si no usas `.venv`, instala las dependencias:

```powershell
pip install -r .\config\requirements.txt
```

## Nota sobre GMP/API

En Greenbone Enterprise Trial 24.10.9 se valido que el appliance no exponia GMP/API por TCP y no mostraba el servicio `GMP` en el menu de GOS. Por eso el flujo recomendado para esta instalacion es exportar el XML desde la interfaz web y convertirlo localmente.

El script conserva soporte experimental para `gvm-cli`, pero el flujo principal y probado es:

```text
Greenbone Web -> XML -> convertir_xml_a_xlsx.bat -> XLSX
```

## Instrucciones en Word

Tambien se incluye una guia de uso en:

```text
Instrucciones_Convertidor_OpenVAS.docx
```
