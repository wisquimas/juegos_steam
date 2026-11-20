@echo off
setlocal
cd /d "%~dp0"

if exist "%~dp0portable\SteamRandom\SteamRandom.exe" (
  "%~dp0portable\SteamRandom\SteamRandom.exe"
  goto :eof
)

if exist "%~dp0dist\juego_random.exe" (
  "%~dp0dist\juego_random.exe"
  goto :eof
)

where python >nul 2>&1
if %errorlevel%==0 (
  python "%~dp0juego_random.py"
  goto :eof
)

echo No se encontro Python ni un .exe portable.
echo Ejecuta build.bat para generar el portable, o instala Python 3.
pause
exit /b 1
