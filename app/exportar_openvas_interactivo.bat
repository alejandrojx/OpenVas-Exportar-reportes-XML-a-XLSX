@echo off
setlocal
cd /d "%~dp0.."

set "BUNDLED_PY=C:\Users\Alejandro\.cache\codex-runtimes\codex-primary-runtime\dependencies\python\python.exe"
set "ROOT=%~dp0.."
set "LOCAL_PY=%ROOT%\.venv\Scripts\python.exe"

if exist "%LOCAL_PY%" (
  "%LOCAL_PY%" "%ROOT%\app\exportar_openvas_interactivo.py"
) else if exist "%BUNDLED_PY%" (
  "%BUNDLED_PY%" "%ROOT%\app\instalar_dependencias.py"
  if exist "%LOCAL_PY%" (
    "%LOCAL_PY%" "%ROOT%\app\exportar_openvas_interactivo.py"
  ) else (
    "%BUNDLED_PY%" "%ROOT%\app\exportar_openvas_interactivo.py"
  )
) else (
  python "%ROOT%\app\instalar_dependencias.py"
  if exist "%LOCAL_PY%" (
    "%LOCAL_PY%" "%ROOT%\app\exportar_openvas_interactivo.py"
  ) else (
    python "%ROOT%\app\exportar_openvas_interactivo.py"
  )
)

echo.
pause
