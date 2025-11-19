import joblib
import numpy as np
from datetime import datetime
from django.shortcuts import render
from tensorflow.keras.models import load_model

MODEL_PATH = "../models/modelo_clima.h5"
SCALER_PATH = "../models/scaler.save"
LABEL_ENCODER_PATH = "../models/label_encoder_classes.npy"
encoder = joblib.load("../models/city_encoder.save")
cities = list(encoder.categories_[0])


model = load_model(MODEL_PATH)
scaler = joblib.load(SCALER_PATH)
label_classes = np.load(LABEL_ENCODER_PATH, allow_pickle=True)



def home(request):
    prediccion = None

    if request.method == "POST":
        try:
            temp = float(request.POST.get("temperature", 0))
            humidity = float(request.POST.get("humidity", 0))
            wind_speed = float(request.POST.get("wind_speed", 0))
            city = request.POST.get("city")
        except ValueError:
            temp = humidity = wind_speed = 0
            city = None

        now = datetime.now()
        hour = now.hour
        month = now.month
        weekday = now.weekday()
        pressure = 1013
        wind_dir = 0

        entrada = np.zeros((1, 17))
        entrada[0,0] = temp
        entrada[0,1] = wind_speed
        entrada[0,2] = wind_dir
        entrada[0,3] = pressure
        entrada[0,4] = humidity
        entrada[0,5] = hour
        entrada[0,6] = month
        entrada[0,7] = weekday

        if city in cities:
            city_idx = cities.index(city)
            entrada[0, 8 + city_idx] = 1

        entrada_scaled = scaler.transform(entrada)

        pred_index = np.argmax(model.predict(entrada_scaled), axis=1)[0]
        prediccion = label_classes[pred_index]

    return render(request, "predictor/home.html", {"prediccion": prediccion, "cities": cities})

