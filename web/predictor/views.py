import joblib
import pandas as pd
import os
from django.shortcuts import render

# Carpeta raíz del proyecto (Proyecto_Clima)
BASE_DIR = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# Ruta absoluta del modelo
MODEL_PATH = os.path.join(BASE_DIR, "models", "modelo_random_forest.pkl")

# Cargar el modelo
model = joblib.load(MODEL_PATH)

def home(request):
    if request.method == "POST":
        temp = float(request.POST.get("temp"))
        humedad = float(request.POST.get("humedad"))
        viento = float(request.POST.get("viento"))

        entrada = pd.DataFrame([{
            "temp": temp,
            "humedad": humedad,
            "viento": viento
        }])

        pred = model.predict(entrada)[0]

        return render(request, "home.html", {"prediccion": pred})

    return render(request, "home.html")
