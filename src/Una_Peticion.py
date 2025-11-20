import requests
import pandas as pd
import os
from dotenv import load_dotenv

load_dotenv()
API_KEY = os.getenv("AEMET_API_KEY")
BASE_URL = "https://opendata.aemet.es/opendata/api/valores/climatologicos/diarios/datos/fechaini/{fechaIni}/fechafin/{fechaFin}/estacion/{idema}"

# --- Configuración de la petición ---
estacion = "5796"      # Código de la estación
year = 2013    # Año que quieres descargar
fecha_ini = f"{2013}-01-01"
fecha_fin = f"{2013}-12-31"

# Construir URL
url = BASE_URL.format(fechaIni=fecha_ini, fechaFin=fecha_fin, idema=estacion)

try:
    # Primera petición: obtiene la URL con los datos reales
    r = requests.get(url, params={"api_key": API_KEY})
    r.raise_for_status()
    datos_json = r.json()
    
    url_datos = datos_json.get("datos")
    if not url_datos:
        print(f"No hay datos para la estación {estacion} en {year}")
    else:
        # Segunda petición: descarga los datos reales
        r2 = requests.get(url_datos)
        r2.raise_for_status()
        datos_estacion = r2.json()
        
        # Guardar en CSV
        df = pd.DataFrame(datos_estacion)
        nombre_csv = f"datos_{estacion}_{year}.csv"
        df.to_csv(nombre_csv, index=False)
        print(f"CSV generado: {nombre_csv} con {len(df)} filas")

except requests.exceptions.RequestException as e:
    print(f"Error al descargar datos: {e}")
