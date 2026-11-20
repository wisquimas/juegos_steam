# Steam Random

Aplicación de consola (Windows) que sortea al azar un juego de tu biblioteca de Steam. Creada por **Wisquimas**.

## Requisitos

- Internet (API de Steam)
- **Steam ID** y **Steam API Key** ([obtener API Key](https://steamcommunity.com/dev/apikey); dominio sugerido: `localhost`)

No hace falta instalar Python si usás el **portable**.

## Uso rápido (portable, sin Python)

1. Descargá el ZIP `SteamRandom-portable.zip` (Release de GitHub o generado con el script de build).
2. Descomprimilo en cualquier carpeta.
3. Ejecutá `SteamRandom.exe`.
4. La primera vez te pedirá Steam ID y API Key; se guardan en `steam_credentials.txt` junto al exe.
5. Respondé `s` / `n` / `saltar` según el juego sorteado.

Los datos locales (`steam_credentials.txt`, `juegos.db`) quedan en la misma carpeta del ejecutable.

## Desarrollo (con Python)

```bat
pip install -r requirements.txt
python juego_random.py
```

O doble clic en `run.bat` (usa el portable si existe; si no, Python del PATH).

## Construir el portable

En Windows, con Python 3.10+ en el PATH:

```bat
build.bat
```

o:

```powershell
.\build_portable.ps1
```

Salida:

| Artefacto | Ruta |
|-----------|------|
| EXE onefile | `dist\juego_random.exe` |
| Carpeta portable | `portable\SteamRandom\SteamRandom.exe` |
| ZIP para distribuir | `portable\SteamRandom-portable.zip` |

El build **no** incluye credenciales ni bases de datos.

## Flujo del programa

1. Sincroniza tu biblioteca Steam y la guarda en `juegos.db`.
2. Si hay un juego **pendiente**, te lo muestra primero.
3. Si no, sortea uno no marcado como jugado.
4. Muestra nombre, descripción, categorías y géneros.
5. `s` = jugado · `saltar` = otro sorteo · `n` = no sortea hasta decidir.

`Ctrl+C` cierra el programa.

## Solución de problemas

- Error de API: revisá Internet, Steam ID y API Key (o borrá `steam_credentials.txt` para reingresarlos).
- Base corrupta: borrá `juegos.db`; se recrea al iniciar.
- Windows Defender / SmartScreen puede avisar en exes sin firma; es normal en builds caseros.

## Privacidad

No subas a GitHub tu `steam_credentials.txt` ni `juegos.db`. Están en `.gitignore`.

## Licencia

Uso personal. No afiliado a Steam ni Valve Corporation.
