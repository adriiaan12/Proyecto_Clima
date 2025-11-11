import pandas as pd
import numpy as np
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import LabelEncoder, StandardScaler, OneHotEncoder
import joblib
import tensorflow as tf
from tensorflow.keras import layers, models

# === 1. Cargar datos ===
data = pd.read_csv("../data/dataset2/all_weather_data.csv")
print("Columnas:", data.columns)
print("Filas:", len(data))

# === 2. Extraer información temporal ===
data['Timestamp'] = pd.to_datetime(data['Timestamp'])
data['Hour'] = data['Timestamp'].dt.hour
data['Month'] = data['Timestamp'].dt.month
data['Weekday'] = data['Timestamp'].dt.weekday

# === 3. Codificar la ciudad (One-Hot) ===
encoder = OneHotEncoder(sparse_output=False) 
city_encoded = encoder.fit_transform(data[['City']])
city_df = pd.DataFrame(city_encoded, columns=encoder.get_feature_names_out(['City']))
data = pd.concat([data, city_df], axis=1)

# === 4. Seleccionar features y target ===
features = ["Temperature (ºC)", "Wind Speed (m/s)", "Wind Direction (degrees)",
            "Pressure (hPa)", "Humidity (%)", "Hour", "Month", "Weekday"] + list(city_df.columns)
target = "Weather"

X = data[features]
y = data[target]

# === 5. Escalar las features numéricas ===
scaler = StandardScaler()
X_scaled = scaler.fit_transform(X)

# Guardar el scaler para usar en predicciones
joblib.dump(scaler, "../models/scaler.save")

# === 6. Codificar el target ===
label_encoder = LabelEncoder()
y_encoded = label_encoder.fit_transform(y)

# Guardar el label encoder
np.save("../models/label_encoder_classes.npy", label_encoder.classes_)

# === 7. Dividir en entrenamiento y test ===
X_train, X_test, y_train, y_test = train_test_split(X_scaled, y_encoded, test_size=0.2, random_state=42)

# === 8. Crear modelo de red neuronal ===
model = models.Sequential([
    layers.Dense(128, activation='relu', input_shape=(X_train.shape[1],)),
    layers.Dense(64, activation='relu'),
    layers.Dense(32, activation='relu'),
    layers.Dense(len(np.unique(y_encoded)), activation='softmax')
])

model.compile(optimizer='adam',
              loss='sparse_categorical_crossentropy',
              metrics=['accuracy'])

# === 9. Entrenar modelo ===
history = model.fit(X_train, y_train,
                    epochs=50,
                    validation_data=(X_test, y_test))

# === 10. Guardar modelo ===
model.save("../models/modelo_clima.h5")
print("✅ Modelo guardado en /models/modelo_clima.h5")
