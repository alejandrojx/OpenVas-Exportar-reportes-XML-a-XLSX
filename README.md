# Exportador OpenVAS / Greenbone a XLSX

Esta carpeta contiene una herramienta para generar reportes `.xlsx` personalizados sin modificar Greenbone OS.

La idea es:

1. Descargar el reporte completo en XML desde Greenbone/OpenVAS.
2. Convertir ese XML a un Excel con hojas de resumen, vulnerabilidades, hosts, CVEs y remediaciÃ³n.
3. Mantener Greenbone intacto para no romper actualizaciones ni firmas de report formats.

## Opcion A: usar un XML ya exportado

En la interfaz de Greenbone, exporta el reporte como `XML` o `Anonymous XML`. Luego ejecuta:

```powershell
python .\openvas_report_to_xlsx.py --xml .\reporte.xml --output .\reporte_openvas.xlsx
```

## Opcion B: descargar por GMP con gvm-cli

Si tienes `gvm-cli` instalado en la maquina desde donde ejecutas el script:

```powershell
python .\openvas_report_to_xlsx.py `
  --gmp-host 192.0.2.10 `
  --gmp-port 9390 `
  --username usuario `
  --password "TU_PASSWORD" `
  --report-id "UUID_DEL_REPORTE" `
  --output .\reporte_openvas.xlsx
```

## Opcion C: modo interactivo para Windows

Tambien puedes ejecutar:

```powershell
.\exportar_openvas_interactivo.bat
```

La primera vez, el `.bat` crea una carpeta local `.venv` e instala `gvm-tools` y `openpyxl`.
Despues de eso ya no pedira la ruta de `gvm-cli`; usara automaticamente:

```text
Exportar_Informe\.venv\Scripts\gvm-cli.exe
```

El asistente te pedira:

- IP o FQDN de Greenbone/OpenVAS
- Puerto GMP, normalmente `9390`
- Usuario
- Password
- Si quieres listar reportes disponibles
- Numero del reporte elegido o UUID manual
- QoD minimo
- Niveles a exportar
- Nombre del XLSX de salida

Si solo escribes un nombre como `reporte_openvas.xlsx`, el archivo se guardara en la carpeta `salidas`.

Para los niveles, puedes usar:

- `hml`: High, Medium y Low
- `chml`: Critical, High, Medium y Low
- `g`: Log

El script usa internamente este formato XML de Greenbone:

```xml
<get_reports report_id="UUID_DEL_REPORTE"
             format_id="a994b278-1f62-11e1-96ac-406186ea4fc5"
             details="1"
             ignore_pagination="1"
             filter="apply_overrides=0 levels=hml rows=0 min_qod=70 first=1 sort-reverse=severity"/>
```

`ignore_pagination="1"` y `rows=0` son importantes para evitar que el reporte quede limitado por las filas que ves en la interfaz.

## Como encontrar el Report ID

En la pagina del reporte de Greenbone, el UUID suele aparecer a la derecha como `ID: ...`.

Tambien puedes listar reportes con `gvm-cli`:

```powershell
gvm-cli tls --hostname 192.0.2.10 --port 9390 `
  --gmp-username usuario --gmp-password "TU_PASSWORD" `
  --xml "<get_reports filter='rows=20 sort-reverse=date'/>"
```

## Error WinError 10060

Si aparece:

```text
[WinError 10060] A connection attempt failed
```

no es un problema del UUID ni del password. Significa que tu equipo no logra abrir conexion TCP al puerto GMP.

Puntos a validar:

- La interfaz web puede responder por `443`, pero `gvm-cli` necesita GMP, normalmente por `9390`.
- El firewall entre tu equipo y Greenbone debe permitir `192.0.2.10:9390`.
- En el appliance GOS, confirma que GMP/API este habilitado o expuesto para tu red.
- Si el appliance no publica GMP remoto, ejecuta este exportador desde una maquina que si tenga acceso al puerto GMP o habilita el acceso en Greenbone.

## Personalizar columnas

El script genera estas hojas:

- `Resumen`
- `Vulnerabilidades`
- `Hosts`
- `CVEs`
- `Remediacion`

Para cambiar columnas, edita la lista `vuln_headers` y el bloque que agrega filas en `openvas_report_to_xlsx.py`.

## Siguiente mejora recomendada

Despues de validar el XLSX, se puede agregar generacion de PDF ejecutivo con logo, portada, tabla de riesgos y plan de remediacion. Lo ideal es crear el PDF desde el mismo XML, no desde el PDF nativo de Greenbone.

