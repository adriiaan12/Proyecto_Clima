import os
import requests
import time
import pandas as pd


from dotenv import load_dotenv

load_dotenv()
API_KEY = os.getenv("AEMET_API_KEY")
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





