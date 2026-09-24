@echo off
setlocal
cd /d "%~dp0"

set "BUNDLED_PYTHON=%USERPROFILE%\.cache\codex-runtimes\codex-primary-runtime\dependencies\python\python.exe"

if exist "%BUNDLED_PYTHON%" (
  "%BUNDLED_PYTHON%" -m venv .venv
) else (
  py -3.12 -m venv .venv 2>nul || python -m venv .venv
)

if not exist ".venv\Scripts\python.exe" (
  echo No se pudo crear el entorno. Instala Python 3.12 o posterior y vuelve a ejecutar este archivo.
  pause
  exit /b 1
)

echo Entorno preparado: .venv\Scripts\python.exe
echo En VS Code selecciona ese interprete si no aparece automaticamente.
pause
