import joblib
import numpy as np
from datetime import datetime
from django.shortcuts import render
import tensorflow as tf


from .utils import obtener_prediccion_adaptada_aemet 


MODEL_PATH = "../models/modelo_clima.h5"
SCALER_PATH = "../models/scaler.save"
LABEL_ENCODER_PATH = "../models/label_encoder_classes.npy"
encoder = joblib.load("../models/city_encoder.save")
cities = list(encoder.categories_[0])


model = tf.keras.models.load_model(MODEL_PATH)
scaler = joblib.load(SCALER_PATH)
label_classes = np.load(LABEL_ENCODER_PATH, allow_pickle=True)



def home(request):
    prediccion = None
    datos_aemet = None
    error_aemet = None
    clase_clima = 'default'

    if request.method == "POST":
        city = request.POST.get("city")

        if city:
            # 1. 🌐 Llamar a la API de AEMET para obtener la predicción real
            datos_aemet = obtener_prediccion_adaptada_aemet(city)
            
            if datos_aemet:
                
                temp = datos_aemet["temperatura"]
                humidity = datos_aemet["humidity"]
                wind_speed = datos_aemet["wind_speed"]
                wind_dir = datos_aemet["wind_dir"]
                

                # Variables temporales/estáticas
                now = datetime.now()
                hour = now.hour
                month = now.month
                weekday = now.weekday()
                pressure = 1013 
                
                # 3. 🔢 Crear el vector de entrada para el modelo
                entrada = np.zeros((1, 17))
                
                # Cargar datos meteorológicos y temporales (índices 0-7)
                entrada[0,0] = temp
                entrada[0,1] = wind_speed
                entrada[0,2] = wind_dir # Dirección en grados (0-360)
                entrada[0,3] = pressure
                entrada[0,4] = humidity
                entrada[0,5] = hour
                entrada[0,6] = month
                entrada[0,7] = weekday
                
                # Codificación One-Hot de la ciudad
                if city in cities:
                    city_idx = cities.index(city)
                    entrada[0, 8 + city_idx] = 1 

                # 4. 🧠 Predecir
                entrada_scaled = scaler.transform(entrada)
                pred_index = np.argmax(model.predict(entrada_scaled), axis=1)[0]
                prediccion = label_classes[pred_index]
                clase_clima = str(label_classes[pred_index])

            else:
                error_aemet = f"No se pudo obtener la predicción para {city}."
    
    
    clase_clima = clase_clima.lower()
    
    # Pasar los datos a la plantilla
    context = {
        "prediccion": prediccion, 
        "cities": cities,
        "error_aemet": error_aemet,
        "clase_clima": clase_clima,
    }
    
    return render(request, "predictor/home.html", context)