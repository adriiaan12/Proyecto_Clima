import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import LabelEncoder, StandardScaler, OneHotEncoder
from sklearn.ensemble import RandomForestClassifier
from sklearn.metrics import accuracy_score, classification_report, confusion_matrix, f1_score
import joblib

# === 1. Cargar datos ===
data = pd.read_csv("../data/dataset2/all_weather_data.csv")
print(f"Datos cargados: {len(data)} filas, {len(data.columns)} columnas")

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
# Guardamos la lista de nombres de features para usarla en el gráfico después
feature_names = ["Temperature (ºC)", "Wind Speed (m/s)", "Wind Direction (degrees)",
            "Pressure (hPa)", "Humidity (%)", "Hour", "Month", "Weekday"] + list(city_df.columns)
target = "Weather"

X = data[feature_names]
y = data[target]

# === 5. Escalar features numéricas ===
scaler = StandardScaler()
X_scaled = scaler.fit_transform(X)
joblib.dump(scaler, "../models/scaler.save")

# === 6. Codificar el target ===
label_encoder = LabelEncoder()
y_encoded = label_encoder.fit_transform(y)
np.save("../models/label_encoder_classes.npy", label_encoder.classes_)

# === 7. Dividir en entrenamiento y test ===
X_train, X_test, y_train, y_test = train_test_split(X_scaled, y_encoded, test_size=0.2, random_state=42)

# === 8. Crear y entrenar Random Forest ===
print("⏳ Entrenando Random Forest (esto puede tardar un poco)...")
rf_model = RandomForestClassifier(n_estimators=200, random_state=42, n_jobs=-1) # n_jobs=-1 usa todos los núcleos de tu CPU
rf_model.fit(X_train, y_train)

# === 9. Evaluar ===
y_pred = rf_model.predict(X_test)

print("\n--- RESULTADOS RANDOM FOREST ---")
acc = accuracy_score(y_test, y_pred)
f1 = f1_score(y_test, y_pred, average='weighted')

print(f"Accuracy: {acc:.4f}")
print(f"F1-Score Global (Weighted): {f1:.4f}")

print("\n--- Reporte de Clasificación ---")
print(classification_report(y_test, y_pred, target_names=label_encoder.classes_, zero_division=0))

# === 10. Guardar modelo ===
joblib.dump(rf_model, "../models/rf_model.save")
print("✅ Random Forest guardado en /models/rf_model.save")

# ==========================================
# === 11. GRÁFICOS ===
# ==========================================

# GRÁFICO 1: Matriz de Confusión [Image of confusion matrix heatmap]
plt.figure(figsize=(10, 8))
cm = confusion_matrix(y_test, y_pred)
sns.heatmap(cm, annot=True, fmt='d', cmap='Oranges', # Usamos Naranja para diferenciar
            xticklabels=label_encoder.classes_,
            yticklabels=label_encoder.classes_)
plt.title('Matriz de Confusión - Random Forest')
plt.xlabel('Predicción')
plt.ylabel('Realidad')
plt.xticks(rotation=45)
plt.tight_layout()
plt.savefig("../models/rf_confusion_matrix.png")
plt.show()

# GRÁFICO 2: Importancia de Características (Feature Importance) [Image of bar chart showing feature importance]
# Esto es exclusivo de árboles de decisión y muy útil para explicar el modelo
importances = rf_model.feature_importances_
indices = np.argsort(importances)[::-1] # Ordenar de mayor a menor

# Tomamos las 10 características más importantes
top_n = 10
top_indices = indices[:top_n]
top_importances = importances[top_indices]
top_names = [feature_names[i] for i in top_indices]

plt.figure(figsize=(10, 6))
sns.barplot(x=top_importances, y=top_names, palette="viridis", hue=top_names, legend=False)
plt.title('Top 10 Variables más Importantes para el Modelo')
plt.xlabel('Importancia Relativa')
plt.tight_layout()
plt.savefig("../models/rf_feature_importance.png")
plt.show()

print("✅ Gráficos generados.")