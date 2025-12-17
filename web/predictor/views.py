import joblib
import numpy as np
import tensorflow as tf
from datetime import datetime
from rest_framework.decorators import api_view
from rest_framework.response import Response
from rest_framework import status

from .utils import obtener_prediccion_adaptada_aemet

#CARGA DE MODELOS
MODEL_PATH = "../models/modelo_clima.h5"
SCALER_PATH = "../models/scaler.save"
LABEL_ENCODER_PATH = "../models/label_encoder_classes.npy"


encoder = joblib.load("../models/city_encoder.save") 
cities = list(encoder.categories_[0])

model = tf.keras.models.load_model(MODEL_PATH)
scaler = joblib.load(SCALER_PATH)
label_classes = np.load(LABEL_ENCODER_PATH, allow_pickle=True)


@api_view(['GET', 'POST'])
def home(request):
    prediccion = "Desconocido"
    datos_aemet = None
    error_aemet = None
    clase_clima = 'default'
    
    # Valores por defecto
    temp = 0
    humidity = 0
    wind_speed = 0
    wind_dir = 0
    
    
    # Si es POST, busca en el cuerpo. Si es GET, busca en ?city=Madrid
    city = request.data.get("city") or request.query_params.get("city")

    # Ciudad por defecto
    if not city:
        city = "Madrid" 

    if city:
        
        datos_aemet = obtener_prediccion_adaptada_aemet(city)
        
        if datos_aemet:
            temp = datos_aemet["temperatura"]
            humidity = datos_aemet["humidity"]
            wind_speed = datos_aemet["wind_speed"]
            wind_dir = datos_aemet["wind_dir"]
            
            # Variables temporales
            now = datetime.now()
            hour = now.hour
            month = now.month
            weekday = now.weekday()
            pressure = 1013 
            
            # 3.Crear vector de entrada
            entrada = np.zeros((1, 17))
            
            entrada[0,0] = temp
            entrada[0,1] = wind_speed
            entrada[0,2] = wind_dir 
            entrada[0,3] = pressure
            entrada[0,4] = humidity
            entrada[0,5] = hour
            entrada[0,6] = month
            entrada[0,7] = weekday
            
            #Encoding Ciudad
            if city in cities:
                city_idx = cities.index(city)
                entrada[0, 8 + city_idx] = 1 

            # 4. 🧠 Predecir
            entrada_scaled = scaler.transform(entrada)
            pred_index = np.argmax(model.predict(entrada_scaled), axis=1)[0]
            
            #Convertir numpy.str_ a string normal de Python para devolverlo en json
            prediccion_raw = label_classes[pred_index]
            prediccion = str(prediccion_raw) 
            clase_clima = str(prediccion_raw).lower()
        else:
            error_aemet = f"No se pudo obtener datos para {city}."

    data = {
        "city": city,
        "prediccion": prediccion, 
        "clase_clima": clase_clima,
        "temperatura": float(temp),
        "humedad": float(humidity),
        "wind_speed": float(wind_speed),
        "wind_dir": float(wind_dir),
        "available_cities": cities,
        "error": error_aemet,
    }
    
    return Response(data)