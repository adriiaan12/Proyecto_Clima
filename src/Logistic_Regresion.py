import pandas as pd
import numpy as np
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import LabelEncoder, StandardScaler, OneHotEncoder
from sklearn.linear_model import LogisticRegression
from sklearn.metrics import accuracy_score, classification_report
import joblib

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

# === 5. Escalar features numéricas ===
scaler = StandardScaler()
X_scaled = scaler.fit_transform(X)
joblib.dump(scaler, "../models/scaler.save")  # útil para predicciones futuras

# === 6. Codificar el target ===
label_encoder = LabelEncoder()
y_encoded = label_encoder.fit_transform(y)
np.save("../models/label_encoder_classes.npy", label_encoder.classes_)

# === 7. Dividir en entrenamiento y test ===
X_train, X_test, y_train, y_test = train_test_split(X_scaled, y_encoded, test_size=0.2, random_state=42)

# === 8. Crear y entrenar Logistic Regression ===
lr_model = LogisticRegression(multi_class='multinomial', solver='lbfgs', max_iter=1000)
lr_model.fit(X_train, y_train)

# === 9. Evaluar ===
y_pred = lr_model.predict(X_test)
print("Logistic Regression Accuracy:", accuracy_score(y_test, y_pred))
print(classification_report(y_test, y_pred))

# === 10. Guardar modelo ===
joblib.dump(lr_model, "../models/lr_model.save")
print("✅ Logistic Regression guardado en /models/lr_model.save")
