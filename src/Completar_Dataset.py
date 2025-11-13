import requests
import pandas as pd
import time
import json

API_KEY = "eyJhbGciOiJIUzI1NiJ9.eyJzdWIiOiJhZHJpYW5zYW5hbDI3QGdtYWlsLmNvbSIsImp0aSI6IjA1MTY0NjAwLTg0NzMtNGNkNC1iZjczLTYyZGEwOWZhMTcyNyIsImlzcyI6IkFFTUVUIiwiaWF0IjoxNzYxMDc5NDk0LCJ1c2VySWQiOiIwNTE2NDYwMC04NDczLTRjZDQtYmY3My02MmRhMDlmYTE3MjciLCJyb2xlIjoiIn0.JwjWB3XH77BfC9Gzt2uGp_o0Ls62wb2WURRCYY7K-BI"
BASE_URL = "https://opendata.aemet.es/opendata/api/valores/climatologicos/diarios/datos/fechaini/{fechaIni}/fechafin/{fechaFin}/estacion/{idema}"

# --- Configuración ---
start_year = 2010
end_year = 2025

# Estaciones de Cádiz
estaciones_cadiz = [
    "5891X", "5835X", "5796", "5790Y", "5783",
    "5733X", "5704B", "5656", "5654X", "5612X",
    "5598X"
]

sleep_time = 10  # Segundos entre peticiones
max_reintentos = 3

all_data = []

def descargar_json(url):
    """Descargar JSON con reintentos en caso de error 429 o problemas temporales."""
    for intento in range(max_reintentos):
        try:
            r = requests.get(url, params={"api_key": API_KEY})
            if r.status_code == 429:
                wait = (intento + 1) * 5  # espera creciente
                print(f"Exceso de peticiones, esperando {wait}s...")
                time.sleep(wait)
                continue
            r.raise_for_status()
            return r.json()
        except requests.exceptions.RequestException as e:
            wait = (intento + 1) * 3
            print(f"Error en petición, reintentando en {wait}s... ({e})")
            time.sleep(wait)
    print(f"No se pudo descargar {url} tras {max_reintentos} intentos")
    return None

for estacion in estaciones_cadiz:
    print(f"\nDescargando datos para estación {estacion}...")
    
    for year in range(start_year, end_year + 1):
        fecha_ini = f"{year}-01-01"
        fecha_fin = f"{year}-12-31"
        url = BASE_URL.format(fechaIni=fecha_ini, fechaFin=fecha_fin, idema=estacion)
        
        datos_json = descargar_json(url)
        if not datos_json:
            continue
        
        url_datos = datos_json.get("datos")
        if not url_datos:
            print(f"No hay datos para {estacion} en {year}")
            continue
        
        datos_estacion = descargar_json(url_datos)
        if not datos_estacion:
            continue
        
        # Mostrar una vista previa del JSON
        print(f"\n=== JSON encontrado para {estacion} en {year} (primeros 2 registros) ===")
        print(json.dumps(datos_estacion[:2], indent=2, ensure_ascii=False))
        
        all_data.extend(datos_estacion)
        print(f"Añadidos {len(datos_estacion)} registros de {year} para {estacion}")
        
        time.sleep(sleep_time)

# Convertir a DataFrame y guardar CSV
df = pd.DataFrame(all_data)
df.to_csv("dataset_clima_cadiz_20años.csv", index=False)
print(f"\nCSV generado con {len(df)} filas.")
