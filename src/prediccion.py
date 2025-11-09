import numpy as np
import tensorflow as tf
from tensorflow.keras.models import load_model
from sklearn.preprocessing import StandardScaler

# === 1. Cargar modelo y clases ===
model = load_model("../models/modelo_clima.h5")
classes = np.load("../models/label_encoder_classes.npy", allow_pickle=True)

# === 2. Función para preprocesar nuevos datos ===
# Recuerda: el modelo espera las mismas columnas que entrenaste
def preprocess_input(data):
    scaler = StandardScaler()
    # Normalizamos según los valores del dataset original
    # NOTA: Para producción, deberías guardar y cargar el scaler usado en entrenamiento
    X_scaled = scaler.fit_transform(data)
    return X_scaled

# === 3. Función para predecir ===
def predict_weather(temp, wind_speed, wind_dir, pressure, humidity):
    # Crear un array con los datos
    new_data = np.array([[temp, wind_speed, wind_dir, pressure, humidity]])
    
    # Preprocesar
    X_scaled = preprocess_input(new_data)
    
    # Predecir
    y_pred = model.predict(X_scaled)
    class_index = np.argmax(y_pred, axis=1)[0]
    weather_class = classes[class_index]
    return weather_class

# === 4. Ejemplo de uso ===
if __name__ == "__main__":

    #Timestamp,Temperature (ºC),Wind Speed (m/s),Wind Direction (degrees),Pressure (hPa),Humidity (%),Weather,City
    pred = predict_weather(1.26, 7.2, 340, 1010, 90)
    print("Predicción del clima:", pred)
