import numpy as np
import pandas as pd
import tensorflow as tf
from tensorflow.keras.models import load_model
import joblib

# === 1. Cargar modelo, clases y scaler ===
model = load_model("../models/modelo_clima.h5")
classes = np.load("../models/label_encoder_classes.npy", allow_pickle=True)
scaler = joblib.load("../models/scaler.save")  # cargar el scaler original

# === 2. Función para predecir ===
def predict_weather(timestamp, city, temp, wind_speed, wind_dir, pressure, humidity):
    # Convertir timestamp a datetime y extraer info temporal
    ts = pd.to_datetime(timestamp)
    hour = ts.hour
    month = ts.month
    weekday = ts.weekday()
    
    # Crear DataFrame con las features numéricas
    df = pd.DataFrame({
        "Temperature (ºC)": [temp],
        "Wind Speed (m/s)": [wind_speed],
        "Wind Direction (degrees)": [wind_dir],
        "Pressure (hPa)": [pressure],
        "Humidity (%)": [humidity],
        "Hour": [hour],
        "Month": [month],
        "Weekday": [weekday]
    })
    
    # Añadir columnas de ciudad codificadas (One-Hot)
    for col in scaler.feature_names_in_:
        if col.startswith("City_"):
            df[col] = 1 if col == f"City_{city}" else 0
    
    # Escalar todas las features
    X_scaled = scaler.transform(df)
    
    # Predecir
    y_pred = model.predict(X_scaled)
    class_index = np.argmax(y_pred, axis=1)[0]
    weather_class = classes[class_index]
    return weather_class


# === 3. Ejemplo de uso ===
#,4.63,340,987,82,Snow
if __name__ == "__main__":
    pred = predict_weather(
        timestamp="2025-11-13 14:00:00",
        city="Murcia",
        temp=25,
        wind_speed=13,
        wind_dir=0,
        pressure=1012,
        humidity=45
    )
    print("Predicción del clima:", pred)
