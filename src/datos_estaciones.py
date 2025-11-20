import os
import requests
import json
import time
from datetime import date, timedelta
from typing import Generator, Dict, Any, List, Optional
from dotenv import load_dotenv

load_dotenv()
API_KEY = os.getenv("AEMET_API_KEY")
# --- Configuración ---
# **IMPORTANTE:** Reemplaza 'TU_API_KEY' con tu clave real de AEMET OpenData


# URL base y endpoint
BASE_URL = "https://opendata.aemet.es/opendata/api/"
ENDPOINT_DATOS = "valores/climatologicos/diarios/datos/fechaini/{fechaIniStr}/fechafin/{fechaFinStr}/todasestaciones"

# Límite de la API y manejo de la pausa
MAX_REQUESTS_PER_MINUTE = 40
# Espera de seguridad entre peticiones (1.6 segundos asegura no superar 37.5/min)
SLEEP_TIME_SECONDS = 1.6 
# Rango máximo de días a pedir en cada consulta
# 🌟 AJUSTADO: Se reduce de 365 a 90 días para mejorar la estabilidad de la consulta en AEMET.
DIAS_POR_CONSULTA = 90 

# --- Funciones de Utilidad ---

def generar_rangos_fechas(fecha_inicio: date, fecha_fin: date, delta_dias: int) -> Generator[Dict[str, str], None, None]:
    """Genera pares de fechas (inicio y fin) para chunkear el periodo total."""
    current_start = fecha_inicio

    # Se añade un pequeño margen de seguridad para evitar pedir datos de hoy
    # ya que los datos climatológicos se consolidan con retraso.
    margen_seguridad = 3
    fecha_limite = date.today() - timedelta(days=margen_seguridad)

    while current_start < fecha_fin and current_start < fecha_limite:
        current_end = current_start + timedelta(days=delta_dias - 1)

        # Aseguramos que el fin del rango no supere la fecha final deseada o el límite de seguridad
        if current_end > fecha_fin:
            current_end = fecha_fin
        if current_end > fecha_limite:
            current_end = fecha_limite

        # Formato 'YYYY-MM-DD' para uso interno
        yield {
            "fecha_ini": current_start.strftime("%Y-%m-%d"),
            "fecha_fin": current_end.strftime("%Y-%m-%d")
        }

        # El inicio del próximo rango es el día después del fin actual
        current_start = current_end + timedelta(days=1)

def obtener_datos_climatologicos(fecha_inicio: str, fecha_fin: str) -> Optional[List[Dict[str, Any]]]:
    """
    Realiza la doble consulta a la API de AEMET para un rango de fechas.
    """
    url_peticion = BASE_URL + ENDPOINT_DATOS.format(
    fechaIniStr=fecha_inicio.replace("-", ""),
    fechaFinStr=fecha_fin.replace("-", "")
    )
 
    headers = {'api_key': API_KEY, 'Content-Type': 'application/json'}

    try:
        # 1. Primera llamada para obtener el enlace de los datos
        response_peticion = requests.get(url_peticion, headers=headers)
        response_peticion.raise_for_status() 
        datos_peticion = response_peticion.json()

        if datos_peticion.get('estado') == 200 and 'datos' in datos_peticion:
            url_datos = datos_peticion['datos']

            # 2. Ejecutar la segunda consulta (obtener los datos reales)
            response_datos = requests.get(url_datos)
            response_datos.raise_for_status()

            return response_datos.json()

        elif datos_peticion.get('estado') == 404:
            print(f"    [INFO] No hay datos disponibles en AEMET para este rango.")
            return [] # Retornar lista vacía para continuar

        else:
            print(f"    [ERROR] Fallo en la primera respuesta: Estado {datos_peticion.get('estado')}, Descripción: {datos_peticion.get('descripcion')}")
            return None

    except requests.exceptions.RequestException as e:
        print(f"    [ERROR] Fallo de conexión o HTTP: {e}")
        return None
    except json.JSONDecodeError:
        print("    [ERROR] Fallo al decodificar la respuesta JSON.")
        return None

# --- Función Principal ---

def crear_dataset_historico(fecha_inicio_historica: date, fecha_fin_historica: date, nombre_archivo: str):
    """
        Orquesta la descarga masiva, respetando los límites de la API.
    """
    if API_KEY == "TU_API_KEY":
        print("🛑 Error: Por favor, introduce tu clave de API en la variable API_KEY.")
        return

    print(f"Iniciando descarga histórica: {fecha_inicio_historica} a {fecha_fin_historica}")

    datos_completos: List[Dict[str, Any]] = []

    # Generar los rangos de fechas (chunks)
    rangos = list(generar_rangos_fechas(fecha_inicio_historica, fecha_fin_historica, DIAS_POR_CONSULTA))
    total_chunks = len(rangos)

    for i, rango in enumerate(rangos):
        f_ini = rango['fecha_ini']
        f_fin = rango['fecha_fin']

        print(f"\n--- Chunk {i + 1}/{total_chunks} ---")
        print(f"  Rango: {f_ini} a {f_fin}")

         # Realizar la consulta para el chunk actual
        datos_chunk = obtener_datos_climatologicos(f_ini, f_fin)

        if datos_chunk is None:
            # Fallo grave, se podría implementar un mecanismo de reintento
            print("  [ADVERTENCIA] Error irrecuperable en el chunk. Se detiene el proceso.")
            break

    if datos_chunk:
            datos_completos.extend(datos_chunk)
            print(f"  Registros añadidos: {len(datos_chunk)}. Total acumulado: {len(datos_completos)}")

    # **RESPETAR LÍMITE DE TASA:** Pausa obligatoria entre cada doble-petición
    print(f"  Haciendo pausa de {SLEEP_TIME_SECONDS} segundos...")
    time.sleep(SLEEP_TIME_SECONDS)
    # Guardar los datos finales
    if datos_completos:
        with open(nombre_archivo, 'w', encoding='utf-8') as f:
            json.dump(datos_completos, f, ensure_ascii=False, indent=4)
        print(f"\n✅ Proceso finalizado. Datos guardados en '{nombre_archivo}' con {len(datos_completos)} registros.")
    else:
        print("\n⚠️ Proceso finalizado. No se pudieron descargar datos.")

# --- Ejemplo de Uso (Desde el 1 de enero de 2020 hasta hace unos días) ---

if __name__ == "__main__":
    # Define el rango histórico deseado:
    INICIO_HISTORICO = date(2020, 1, 1) # Por ejemplo, 1 de enero de 2020
    FIN_HISTORICO = date.today() # Hasta hoy (la función lo ajustará con el margen de seguridad)
    NOMBRE_ARCHIVO_SALIDA = "clima_historico_aemet.json"

    crear_dataset_historico(INICIO_HISTORICO, FIN_HISTORICO, NOMBRE_ARCHIVO_SALIDA)