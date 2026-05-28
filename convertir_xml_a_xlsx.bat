@echo off
setlocal
cd /d "%~dp0"

set "BUNDLED_PY=C:\Users\Alejandro\.cache\codex-runtimes\codex-primary-runtime\dependencies\python\python.exe"
set "LOCAL_PY=%~dp0.venv\Scripts\python.exe"

if exist "%LOCAL_PY%" (
  "%LOCAL_PY%" -c "import openpyxl, reportlab" >nul 2>nul
  if errorlevel 1 (
    "%LOCAL_PY%" "%~dp0app\instalar_dependencias.py"
  )
  "%LOCAL_PY%" "%~dp0app\convertir_xml_interactivo.py"
) else if exist "%BUNDLED_PY%" (
  "%BUNDLED_PY%" "%~dp0app\instalar_dependencias.py"
  "%BUNDLED_PY%" "%~dp0app\convertir_xml_interactivo.py"
) else (
  python "%~dp0app\instalar_dependencias.py"
  python "%~dp0app\convertir_xml_interactivo.py"
)

echo.
pause
