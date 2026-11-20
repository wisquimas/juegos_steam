# Construye Steam Random portable (PyInstaller onefile) y un ZIP listo para distribuir.
# Requisitos: Python 3.10+ con pip. No incluye credenciales ni bases de datos.

$ErrorActionPreference = "Stop"
Set-Location -Path $PSScriptRoot

Write-Host "==> Instalando dependencias de build..." -ForegroundColor Cyan
python -m pip install -r requirements.txt --quiet

Write-Host "==> Limpiando builds anteriores..." -ForegroundColor Cyan
Remove-Item -Recurse -Force -ErrorAction SilentlyContinue .\build, .\dist, .\portable

Write-Host "==> Compilando con PyInstaller (onefile)..." -ForegroundColor Cyan
python -m PyInstaller --noconfirm --clean .\juego_random.spec

$exe = Join-Path $PSScriptRoot "dist\juego_random.exe"
if (-not (Test-Path $exe)) {
    throw "No se genero dist\juego_random.exe"
}

$portableDir = Join-Path $PSScriptRoot "portable\SteamRandom"
New-Item -ItemType Directory -Force -Path $portableDir | Out-Null
Copy-Item $exe (Join-Path $portableDir "SteamRandom.exe")
Copy-Item (Join-Path $PSScriptRoot "README.md") (Join-Path $portableDir "README.md")

$zipPath = Join-Path $PSScriptRoot "portable\SteamRandom-portable.zip"
if (Test-Path $zipPath) { Remove-Item $zipPath -Force }
Compress-Archive -Path $portableDir -DestinationPath $zipPath -Force

Write-Host ""
Write-Host "Listo." -ForegroundColor Green
Write-Host "  EXE:  $exe"
Write-Host "  ZIP:  $zipPath"
Write-Host "Distribui el ZIP. El usuario solo necesita descomprimir y ejecutar SteamRandom.exe"
