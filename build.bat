@echo off
setlocal
cd /d "%~dp0"
powershell -NoProfile -ExecutionPolicy Bypass -File "%~dp0build_portable.ps1"
if errorlevel 1 (
  echo.
  echo El build fallo. Revisa que Python y pip esten en el PATH.
  pause
  exit /b 1
)
echo.
pause
