import os
import requests
import pandas as pd
import time
import jsonfrom 
from dotenv import load_dotenv

load_dotenv()
API_KEY = os.getenv("AEMET_API_KEY")
# Endpoints
BASE_DIARIOS_ESTACION = "https://opendata.aemet.es/opendata/api/valores/climatologicos/diarios/datos/fechaini/{fechaIni}/fechafin/{fechaFin}/estacion/{idema}"
BASE_INVENTARIO_ESTACION = "https://opendata.aemet.es/opendata/api/valores/climatologicos/inventarioestaciones/estaciones/{idema}"



# Configuración
estaciones_cadiz = [
    "3104Y", "3129", "3126Y", "3125Y", "3110C",
    "3111D", "3100B", "3170Y", "3175", "3182Y", 
    "3191E","3194U", "3194Y", "3195", "3196","3229Y", 
    "3266A", "3268C", "3330Y", "3338", "3343Y"
]

sleep_time = 1  # segundos entre peticiones
max_reintentos = 3
contador_peticiones = 0
limite_peticiones = 39

all_data = []

# ---------------- Funciones ----------------

def controlar_limite():
    global contador_peticiones
    if contador_peticiones >= limite_peticiones:
        print("\n🟡 Límite de 39 peticiones alcanzado. Esperando 60 segundos...\n")
        time.sleep(60)
        contador_peticiones = 0

def descargar_json(url):
    """Descarga JSON con reintentos usando headers de API_KEY"""
    global contador_peticiones
    headers = {"api_key": API_KEY}
    for intento in range(max_reintentos):
        try:
            controlar_limite()
            r = requests.get(url, headers=headers)
            contador_peticiones += 1

            if r.status_code == 429:
                print("Exceso de peticiones (429), esperando 60s...")
                time.sleep(60)
                continue
            elif r.status_code == 404:
                return None

            r.raise_for_status()
            return r.json()
        except requests.exceptions.RequestException as e:
            wait = (intento + 1) * 5
            print(f"Error en petición, reintentando en {wait}s... ({e})")
            time.sleep(wait)
    print(f"No se pudo descargar {url} tras {max_reintentos} intentos")
    return None

def obtener_anios_estacion(estacion):
    """Obtiene años disponibles según inventario"""
    url = BASE_INVENTARIO_ESTACION.format(idema=estacion)
    inventario_url_json = descargar_json(url)
    if not inventario_url_json or "datos" not in inventario_url_json:
        return []

    inventario = descargar_json(inventario_url_json["datos"])
    if not inventario:
        return []

    fechas = []
    for est in inventario:
        if "fecha_inicio" not in est:
            continue
        inicio = int(est["fecha_inicio"][:4])
        fin = int(est.get("fecha_fin", "2025")[:4])
        fechas.append((inicio, fin))
    return fechas

# ---------------- Proceso principal ----------------

for estacion in estaciones_cadiz:
    print(f"\n📡 Descargando datos para estación {estacion}...")

    rangos_anios = obtener_anios_estacion(estacion)
    if not rangos_anios:
        print(f"No se pudo obtener inventario para {estacion}, saltando...")
        continue

    for inicio, fin in rangos_anios:
        for year in range(inicio, fin + 1):
            fecha_ini = f"{year}-01-01"
            fecha_fin = f"{year}-12-31"
            url = BASE_DIARIOS_ESTACION.format(fechaIni=fecha_ini, fechaFin=fecha_fin, idema=estacion)

            datos_json = descargar_json(url)
            if not datos_json or "datos" not in datos_json:
                print(f"No hay datos para {estacion} en {year}")
                continue

            url_datos = datos_json["datos"]
            print(f"\n✅ Datos disponibles: {url_datos}")

            datos_estacion = descargar_json(url_datos)
            if not datos_estacion:
                print(f"No se pudo descargar datos desde {url_datos}")
                continue

            all_data.extend(datos_estacion)
            print(f"Añadidos {len(datos_estacion)} registros de {year} para {estacion}")

            time.sleep(sleep_time)

# Guardar CSV final
df = pd.DataFrame(all_data)
df.to_csv("dataset_clima_cadiz_completo.csv", index=False)
print(f"\n✅ CSV generado con {len(df)} filas.")
