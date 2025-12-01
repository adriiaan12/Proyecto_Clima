import os
from dotenv import load_dotenv
import requests
import json
from typing import List, Dict, Any
from datetime import datetime
import time

load_dotenv()

BASE_URL = "https://opendata.aemet.es/opendata/api"
API_KEY = os.getenv("AEMET_API_KEY") 


CODIGOS_MUNICIPIO = {
    "Madrid": "28079",
    "Barcelona": "08019",
    "Valencia": "46250",
    "Sevilla": "41091",
    "Zaragoza": "50297",
    "Malaga": "29067",
    "Murcia": "30030",
    "Valladolid": "47141",
    "Bilbao": "48020",
}


DIRECCION_GRADOS = {
    'N': 0, 'NE': 45, 'E': 90, 'SE': 135, 'S': 180, 'SO': 225, 'O': 270, 'NO': 315,
    'C': 0, '': 0
}

def cardinal_a_grados(direccion_aemet: str) -> float:
    direccion = direccion_aemet.upper() if isinstance(direccion_aemet, str) else ''
    return DIRECCION_GRADOS.get(direccion, 0.0) 


def guardar_como_json(datos_aemet: List[Dict[str, Any]], nombre_archivo: str):
    try:
        with open(nombre_archivo, 'w', encoding='utf-8') as f:
            json.dump(datos_aemet, f, indent=4, ensure_ascii=False)
        print(f"✅ Datos crudos guardados exitosamente en: {nombre_archivo}")
    except Exception as e:
        print(f"❌ Error al guardar el archivo JSON: {e}")


def obtener_periodo_segun_hora(hora_actual: int) -> str:
    """Devuelve el periodo de 6 horas de AEMET basado en la hora actual (0-23)."""
    if 0 <= hora_actual < 6:
        return "00-06"
    elif 6 <= hora_actual < 12:
        return "06-12"
    elif 12 <= hora_actual < 18:
        return "12-18"
    else: # 18 <= hora_actual < 24
        return "18-24"



def obtener_prediccion_adaptada_aemet(nombre_municipio: str) -> Dict[str, Any] | None:
    
    cod_municipio = CODIGOS_MUNICIPIO.get(nombre_municipio)
    
    if not cod_municipio:
        print(f"Código AEMET no encontrado para {nombre_municipio}.")
        return None
    
    # Parámetros de reintento
    MAX_REINTENTOS = 3
    TIEMPO_ESPERA = 2 # Espera de 2 segundos entre intentos
    
    try:
        # 1. Obtener la URL de los datos
        url_prediccion = f"{BASE_URL}/prediccion/especifica/municipio/diaria/{cod_municipio}?api_key={API_KEY}"
        
        response_inicial = requests.get(url_prediccion) 
        response_inicial.raise_for_status()
        data_inicial = response_inicial.json()

        if data_inicial.get('estado') != 200 or 'datos' not in data_inicial:
            print(f"Error en la respuesta inicial de AEMET: {data_inicial.get('descripcion', 'N/A')}")
            return None

        url_datos = data_inicial['datos']
        data_prediccion = None

        # 2. Obtener los datos reales con REINTENTO SÍNCRONO
        for intento in range(MAX_REINTENTOS):
            try:
                print(f"Intento {intento + 1}/{MAX_REINTENTOS}: Accediendo a la URL de datos...")
                
                response_datos = requests.get(url_datos) 
                response_datos.raise_for_status() 
                
                # 🛑 Manejo de Decodificación/JSON
                data_prediccion = response_datos.json()
                
                print("Datos obtenidos con éxito.")
                break # Éxito: salimos del bucle
                
            except json.JSONDecodeError as e:
                # Si falla la decodificación (codificación incorrecta o no es JSON)
                try:
                    # Forzamos la decodificación a Latin-1 para ver el mensaje de error en español
                    error_content = response_datos.content.decode('latin-1', errors='replace')
                except:
                    error_content = "[Contenido binario o ilegible]"
                
                print("-" * 50)
                print(f"3. FALLO: Respuesta NO es JSON. Error: {e}. Contenido:")
                print(error_content) 
                print("-" * 50)
                
                if intento < MAX_REINTENTOS - 1:
                    print(f"Esperando {TIEMPO_ESPERA}s y reintentando...")
                    time.sleep(TIEMPO_ESPERA) # Pausa SÍNCRONA
                else:
                    print("Fallo fatal: La respuesta sigue sin ser un JSON válido.")
                    return None
                    
            except requests.exceptions.HTTPError as e:
                # Capturamos errores HTTP (404, 429, 500)
                if intento < MAX_REINTENTOS - 1:
                    print(f"Advertencia: HTTP Error ({e}). Esperando {TIEMPO_ESPERA}s...")
                    time.sleep(TIEMPO_ESPERA) # Pausa SÍNCRONA
                else:
                    print(f"Error fatal: Falló después de {MAX_REINTENTOS} intentos: {e}")
                    return None
        
        if data_prediccion is None:
            return None

        # --- 3. Extracción y Adaptación de Datos ---
        
        # 💾 Opcional: Guardar el JSON crudo (opción para activar si se necesita)
        # nombre_archivo_salida = f"prediccion_cruda_{nombre_municipio}_{cod_municipio}.json"
        # guardar_como_json(data_prediccion, nombre_archivo_salida) 
        
        if not data_prediccion or 'prediccion' not in data_prediccion[0] or not data_prediccion[0]['prediccion']['dia']:
             print("No se encontraron datos de predicción diaria en el JSON.")
             return None

        primer_dia = data_prediccion[0]['prediccion']['dia'][0]
        
        # Temperatura (Promedio simple)
        temp_max = primer_dia['temperatura']['maxima']
        temp_min = primer_dia['temperatura']['minima']
        temperatura = (temp_max + temp_min) / 2
        
        # Humedad Relativa (Promedio simple)
        hum_max = primer_dia['humedadRelativa']['maxima']
        hum_min = primer_dia['humedadRelativa']['minima']
        humidity = (hum_max + hum_min) / 2
        
        # Viento y Dirección: BUSCAR POR EL PERIODO DE 6 HORAS
        hora_actual = datetime.now().hour
        periodo_viento = obtener_periodo_segun_hora(hora_actual)
        viento_periodo = next((v for v in primer_dia['viento'] if v.get('periodo') == periodo_viento), None)
        
        velocidad_viento_kmh = 0
        direccion_viento_aemet = 'C'
        
        if viento_periodo:
            velocidad = viento_periodo.get('velocidad') 
            try:
                velocidad_viento_kmh = int(velocidad) if velocidad not in ["", None] else 0
            except (ValueError, TypeError):
                velocidad_viento_kmh = 0
                
            direccion_viento_aemet = viento_periodo.get('direccion', 'C')

        # CONVERSIÓN: km/h a m/s
        wind_speed_ms = velocidad_viento_kmh / 3.6
        
        # CONVERSIÓN: Cardinal a Grados (0-360)
        wind_dir_grados = cardinal_a_grados(direccion_viento_aemet)


        # 5. Devolver diccionario final con la clase incluida
        return {
            "temperatura": temperatura, 
            "humidity": humidity, 
            "wind_speed": wind_speed_ms,
            "wind_dir": wind_dir_grados,
        }
        
    except requests.exceptions.RequestException as e:
        print(f"❌ Error de solicitud HTTP general (fuera del reintento): {e}")
        return None
    except Exception as e:
        print(f"❌ Error al procesar la predicción: {e}")
        return None