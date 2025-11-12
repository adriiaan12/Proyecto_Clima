import numpy as np
import pandas as pd
import joblib

# === 1. Cargar modelo, clases y scaler ===
model = joblib.load("../models/rf_model.save")  # modelo de Random Forest
classes = np.load("../models/label_encoder_classes.npy", allow_pickle=True)
scaler = joblib.load("../models/scaler.save")  # scaler usado durante el entrenamiento

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
    # Usamos las columnas que el scaler vio durante el entrenamiento
    for col in scaler.feature_names_in_:
        if col.startswith("City_"):
            df[col] = 1 if col == f"City_{city}" else 0

    # Escalar todas las features (como durante el entrenamiento)
    X_scaled = scaler.transform(df)

    # Predecir con Random Forest
    y_pred = model.predict(X_scaled)
    weather_class = classes[int(y_pred[0])]
    return weather_class


# === 3. Ejemplo de uso ===
if __name__ == "__main__":
    pred = predict_weather(
        timestamp="2025-11-12 14:00:00",
        city="Murcia",
        temp=22,
        wind_speed=11,
        wind_dir=340,
        pressure=1015,
        humidity=53
    )
    print("🌤️ Predicción del clima:", pred)
