import os
import requests
import json

from dotenv import load_dotenv

load_dotenv()
API_KEY = os.getenv("AEMET_API_KEY")
BASE_URL = "https://opendata.aemet.es/opendata/api"

def obtener_prediccion_municipio(cod_municipio):
    url = f"{BASE_URL}/prediccion/especifica/municipio/diaria/{cod_municipio}?api_key={API_KEY}"
    response = requests.get(url)
    
    if response.status_code != 200:
        print("Error al conectar con AEMET:", response.status_code)
        return
    
    # La respuesta devuelve un JSON con un enlace a los datos reales
    datos = response.json()
    if "datos" not in datos:
        print("No hay datos disponibles")
        return
    
    url_datos = datos["datos"]  # Aquí se encuentra la URL con la información real
    response_datos = requests.get(url_datos)
    prediccion = response_datos.json()
    
    return prediccion



# Ejemplo: Predicción diaria de Sevilla
prediccion_ciudad = obtener_prediccion_municipio("41091")
print(json.dumps(prediccion_ciudad, indent=2, ensure_ascii=False))

# Recorrer los días
for dia in prediccion_ciudad[0]["prediccion"]["dia"]:
    print(f"Fecha: {dia['fecha']}")
    
    # Probabilidad de precipitación por periodos
    for p in dia.get("probPrecipitacion", []):
        periodo = p.get("periodo", "00-24")  # valor por defecto si no existe
        value = p.get("value", 0)
        print(f"  Periodo {periodo}: {value}% precipitación")
    
    # Estado del cielo por periodos
    for e in dia.get("estadoCielo", []):
        periodo = e.get("periodo", "00-24")
        descripcion = e.get("descripcion", "")
        print(f"  Periodo {periodo} - {descripcion}")
    
    # Temperatura máxima y mínima
    temp = dia.get("temperatura", {})
    print(f"  Temp máxima: {temp.get('maxima','')} , mínima: {temp.get('minima','')}")
    
    print("-" * 40)
