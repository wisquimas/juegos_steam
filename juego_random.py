import requests
import random
import sqlite3
import datetime
import os
import sys

presiona_enter_global = 1


def app_dir():
    """Carpeta de datos junto al .exe (portable) o al script."""
    if getattr(sys, "frozen", False):
        return os.path.dirname(sys.executable)
    return os.path.dirname(os.path.abspath(__file__))


BASE_DIR = app_dir()
CREDENTIALS_FILE = os.path.join(BASE_DIR, "steam_credentials.txt")
DB_FILE = os.path.join(BASE_DIR, "juegos.db")

def mostrar_titulo():
    titulo = """
    \033[1m
███████╗████████╗███████╗ █████╗ ███╗   ███╗    ██████╗  █████╗ ███╗   ██╗██████╗  ██████╗ ███╗   ███╗
██╔════╝╚══██╔══╝██╔════╝██╔══██╗████╗ ████║    ██╔══██╗██╔══██╗████╗  ██║██╔══██╗██╔═══██╗████╗ ████║
███████╗   ██║   █████╗  ███████║██╔████╔██║    ██████╔╝███████║██╔██╗ ██║██║  ██║██║   ██║██╔████╔██║
╚════██║   ██║   ██╔══╝  ██╔══██║██║╚██╔╝██║    ██╔══██╗██╔══██║██║╚██╗██║██║  ██║██║   ██║██║╚██╔╝██║
███████║   ██║   ███████╗██║  ██║██║ ╚═╝ ██║    ██║  ██║██║  ██║██║ ╚████║██████╔╝╚██████╔╝██║ ╚═╝ ██║
╚══════╝   ╚═╝   ╚══════╝╚═╝  ╚═╝╚═╝     ╚═╝    ╚═╝  ╚═╝╚═╝  ╚═╝╚═╝  ╚═══╝╚═════╝  ╚═════╝ ╚═╝     ╚═╝
                                                                                  Creado por Wisquimas
    \033[0m
    """
    print(titulo)

# Cargar Steam API Key y Steam ID de un archivo o pedirlos desde la consola
def cargar_credenciales():
    if os.path.exists(CREDENTIALS_FILE):
        with open(CREDENTIALS_FILE, 'r', encoding='utf-8') as f:
            steam_id = f.readline().strip()
            steam_api_key = f.readline().strip()
    else:
        steam_id = input("Ingresa tu Steam ID: ")
        steam_api_key = input("Ingresa tu Steam API Key: ")
        with open(CREDENTIALS_FILE, 'w', encoding='utf-8') as f:
            f.write(f"{steam_id}\n{steam_api_key}\n")
    return steam_id, steam_api_key

# Obtener la lista de juegos desde Steam
def obtener_lista_de_juegos(steam_id, steam_api_key):
    try:
        url = f"http://api.steampowered.com/IPlayerService/GetOwnedGames/v0001/?key={steam_api_key}&steamid={steam_id}&format=json&include_appinfo=true"
        response = requests.get(url)
        response.raise_for_status()  # Lanzar excepción si hay un error en la respuesta
        data = response.json()
        juegos = data['response']['games']
        return [{'id': juego['appid'], 'nombre': juego['name']} for juego in juegos]
    except requests.exceptions.RequestException as e:
        print(f"Error al conectar con la API de Steam: {e}")
        steam_id = input("Ingresa tu Steam ID: ")
        steam_api_key = input("Ingresa tu Steam API Key: ")
        with open(CREDENTIALS_FILE, 'w', encoding='utf-8') as f:
            f.write(f"{steam_id}\n{steam_api_key}\n")
        return obtener_lista_de_juegos(steam_id, steam_api_key)

# Obtener detalles de un juego específico (descripción, etiquetas y categorías)
def obtener_detalles_juego(appid):
    try:
        url = f"https://store.steampowered.com/api/appdetails?appids={appid}"
        response = requests.get(url)
        response.raise_for_status()
        data = response.json()

        if data[str(appid)]['success']:
            detalles = data[str(appid)]['data']
            descripcion = detalles.get('short_description', 'Descripción no disponible')
            categorias = [categoria['description'] for categoria in detalles.get('categories', [])]
            generos = [genero['description'] for genero in detalles.get('genres', [])]
            return descripcion, categorias, generos
        else:
            return "Descripción no disponible", [], []
    except Exception as e:
        print(f"Error al obtener detalles del juego {appid}: {e}")
        return "Descripción no disponible", [], []

# Crear o inicializar la base de datos
def crear_base_de_datos():
    try:
        conn = sqlite3.connect(DB_FILE)
        c = conn.cursor()
        c.execute('''
            CREATE TABLE IF NOT EXISTS juegos (
                id INTEGER PRIMARY KEY,
                nombre TEXT,
                jugado INTEGER DEFAULT 0,
                fecha_sorteo TEXT,
                pendiente INTEGER DEFAULT 0
            )
        ''')
        conn.commit()
        conn.close()
    except Exception as e:
        print(f"Error al crear la base de datos: {e}")

# Guardar juegos en la base de datos
def guardar_juegos(juegos):
    try:
        conn = sqlite3.connect(DB_FILE)
        c = conn.cursor()
        for juego in juegos:
            c.execute('INSERT OR IGNORE INTO juegos (id, nombre) VALUES (?, ?)', (juego['id'], juego['nombre']))
        conn.commit()
        conn.close()
    except Exception as e:
        print(f"Error al guardar juegos en la base de datos: {e}")

# Registrar la fecha y hora del sorteo, y marcarlo como pendiente
def registrar_sorteo(juego_id):
    try:
        conn = sqlite3.connect(DB_FILE)
        c = conn.cursor()
        fecha_actual = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        c.execute("UPDATE juegos SET fecha_sorteo = ?, pendiente = 1 WHERE id = ?", (fecha_actual, juego_id))
        conn.commit()
        conn.close()
    except Exception as e:
        print(f"Error al registrar el sorteo: {e}")

# Obtener el último juego pendiente
def obtener_juego_pendiente():
    try:
        conn = sqlite3.connect(DB_FILE)
        c = conn.cursor()
        c.execute("SELECT id, nombre FROM juegos WHERE pendiente = 1 LIMIT 1")
        juego = c.fetchone()
        conn.close()
        return juego
    except Exception as e:
        print(f"Error al obtener el último juego pendiente: {e}")
        return None

# Seleccionar un juego random que no haya sido jugado
def seleccionar_juego_random():
    try:
        conn = sqlite3.connect(DB_FILE)
        c = conn.cursor()
        c.execute("SELECT id, nombre FROM juegos WHERE jugado = 0 ORDER BY RANDOM() LIMIT 1")
        juego = c.fetchone()
        if juego:
            registrar_sorteo(juego[0])  # Registrar la fecha del sorteo y marcar como pendiente
        conn.close()
        return juego if juego else None
    except Exception as e:
        print(f"Error al seleccionar un juego random: {e}")
        return None

# Marcar un juego como jugado y limpiar el pendiente
def marcar_como_jugado(juego_id):
    try:
        conn = sqlite3.connect(DB_FILE)
        c = conn.cursor()
        c.execute("UPDATE juegos SET jugado = 1, pendiente = 0 WHERE id = ?", (juego_id,))
        conn.commit()
        conn.close()
    except Exception as e:
        print(f"Error al marcar el juego como jugado: {e}")

# Saltar el juego, sin marcarlo como jugado, pero limpiando el pendiente
def saltar_juego(juego_id):
    try:
        conn = sqlite3.connect(DB_FILE)
        c = conn.cursor()
        c.execute("UPDATE juegos SET pendiente = 0 WHERE id = ?", (juego_id,))
        conn.commit()
        conn.close()
    except Exception as e:
        print(f"Error al saltar el juego: {e}")

def escribir_info_juego(juego):
    # Obtener los detalles del juego sorteado
    descripcion, categorias, generos = obtener_detalles_juego(juego[0])
    # Imprimir el juego sorteado y sus detalles con formato
    print(f"\n\033[1mJuego seleccionado\033[0m: \033[93m{juego[1]}\033[0m")
    print(f"\033[1mDescripción\033[0m: {descripcion}")
    print(f"\033[1mCategorías\033[0m: {', '.join(categorias) if categorias else 'No disponibles'}")
    print(f"\033[1mGéneros\033[0m: {', '.join(generos) if generos else 'No disponibles'}\n")

def consultar_sobre_juego(juego):
    global presiona_enter_global
    # Obtener los detalles del juego sorteado
    escribir_info_juego(juego)

    respuesta = input(f"¿Jugaste \033[93m{juego[1]}\033[0m? \033[1m(s/n/saltar)\033[0m: ").lower()
    if respuesta == 's':
        marcar_como_jugado(juego[0])
        print(f"Marcaste {juego[1]} como jugado.")
    elif respuesta == 'saltar':
        saltar_juego(juego[0])
        print(f"Saltaste {juego[1]}.")
        presiona_enter_global = 0
    else:
        print(f"No podés sortear otro juego hasta que marques {juego[1]} como jugado o lo saltes.")
        return

# Programa principal
def jugar():
    global presiona_enter_global
    try:
        mostrar_titulo()
        crear_base_de_datos()

        # Obtener las credenciales de Steam
        steam_id, steam_api_key = cargar_credenciales()

        # Obtener la lista de juegos desde Steam
        print("Obteniendo lista de juegos desde Steam...")
        juegos = obtener_lista_de_juegos(steam_id, steam_api_key)
        if juegos:
            print(f"Juegos obtenidos: {len(juegos)}")
            guardar_juegos(juegos)
        else:
            print("No se pudieron obtener juegos o la lista está vacía.")

        while True:
            # Verificar si hay un juego pendiente
            juego_pendiente = obtener_juego_pendiente()
            if juego_pendiente:
                consultar_sobre_juego(juego_pendiente)
            else:
                if presiona_enter_global != 0:
                    input("Presioná enter para sortear un juego...")

                presiona_enter_global = 1
                juego = seleccionar_juego_random()
                if not juego:
                    print("Ya jugaste todos los juegos o no hay juegos disponibles!")
                    break
                consultar_sobre_juego(juego)

    except KeyboardInterrupt:
        print("\nPrograma terminado por el usuario.")
    except Exception as e:
        print(f"Ocurrió un error inesperado: {e}")

# Ejecutar el programa
if __name__ == "__main__":
    jugar()

