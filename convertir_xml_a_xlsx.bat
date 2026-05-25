@echo off
setlocal
cd /d "%~dp0"

set "BUNDLED_PY=C:\Users\Alejandro\.cache\codex-runtimes\codex-primary-runtime\dependencies\python\python.exe"
set "LOCAL_PY=%~dp0.venv\Scripts\python.exe"

if exist "%LOCAL_PY%" (
  "%LOCAL_PY%" "%~dp0app\convertir_xml_interactivo.py"
) else if exist "%BUNDLED_PY%" (
  "%BUNDLED_PY%" "%~dp0app\convertir_xml_interactivo.py"
) else (
  python "%~dp0app\convertir_xml_interactivo.py"
)

echo.
pause
