import pandas as pd
import numpy as np
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import LabelEncoder, StandardScaler
import tensorflow as tf
from tensorflow.keras import layers, models

# === 1. Cargar datos ===
data = pd.read_csv("../data/dataset2/all_weather_data.csv")
print("Columnas:", data.columns)
print("Filas:", len(data))

# === 2. Seleccionar características y variable objetivo ===
features = ["Temperature (ºC)", "Wind Speed (m/s)", "Wind Direction (degrees)", "Pressure (hPa)", "Humidity (%)"]
target = "Weather"

X = data[features]
y = data[target]

# === 3. Codificar etiquetas (ej: 'Sunny', 'Rain', 'Cloudy'...) ===
label_encoder = LabelEncoder()
y_encoded = label_encoder.fit_transform(y)

# === 4. Escalar los datos numéricos ===
scaler = StandardScaler()
X_scaled = scaler.fit_transform(X)

# === 5. Dividir en entrenamiento y test ===
X_train, X_test, y_train, y_test = train_test_split(X_scaled, y_encoded, test_size=0.2, random_state=42)

# === 6. Crear modelo simple de red neuronal ===
model = models.Sequential([
    layers.Dense(64, activation='relu', input_shape=(X_train.shape[1],)),
    layers.Dense(32, activation='relu'),
    layers.Dense(len(np.unique(y_encoded)), activation='softmax')
])

model.compile(optimizer='adam',
              loss='sparse_categorical_crossentropy',
              metrics=['accuracy'])


# === 7. Entrenar ===
history = model.fit(X_train, y_train, epochs=30, validation_data=(X_test, y_test))



# === 8. Guardar modelo y transformadores ===
model.save("../models/modelo_clima.h5")
np.save("../models/label_encoder_classes.npy", label_encoder.classes_)
print("✅ Modelo guardado en /models/modelo_clima.h5")
