import requests
import time
import pandas as pd


API_KEY = "eyJhbGciOiJIUzI1NiJ9.eyJzdWIiOiJhZHJpYW5zYW5hbDI3QGdtYWlsLmNvbSIsImp0aSI6IjA1MTY0NjAwLTg0NzMtNGNkNC1iZjczLTYyZGEwOWZhMTcyNyIsImlzcyI6IkFFTUVUIiwiaWF0IjoxNzYxMDc5NDk0LCJ1c2VySWQiOiIwNTE2NDYwMC04NDczLTRjZDQtYmY3My02MmRhMDlmYTE3MjciLCJyb2xlIjoiIn0.JwjWB3XH77BfC9Gzt2uGp_o0Ls62wb2WURRCYY7K-BI"
BASE_URL = "https://opendata.aemet.es/opendata/api/valores/climatologicos/inventarioestaciones/todasestaciones"

# Paso 1: Llamar a la API
url = f"{BASE_URL}?api_key={API_KEY}"
r = requests.get(url)
r.raise_for_status()
datos = r.json()

# Paso 2: Obtener la URL real de los datos
url_datos = datos.get("datos")
r2 = requests.get(url_datos)
r2.raise_for_status()
estaciones = r2.json()

# Paso 3: Mostrar listado
for e in estaciones:
    print(f"{e.get('provincia')} - {e.get('municipio')} - {e.get('nombre')} (Código: {e.get('indicativo')})")

print(f"\nTotal estaciones: {len(estaciones)}")





