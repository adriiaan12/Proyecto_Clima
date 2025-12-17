import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import LabelEncoder, StandardScaler, OneHotEncoder
from sklearn.linear_model import LogisticRegression
from sklearn.metrics import accuracy_score, classification_report, confusion_matrix, f1_score
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
joblib.dump(scaler, "../models/scaler.save")

# === 6. Codificar el target ===
label_encoder = LabelEncoder()
y_encoded = label_encoder.fit_transform(y)
np.save("../models/label_encoder_classes.npy", label_encoder.classes_)

# === 7. Dividir en entrenamiento y test ===
X_train, X_test, y_train, y_test = train_test_split(X_scaled, y_encoded, test_size=0.2, random_state=42)

# === 8. Crear y entrenar Logistic Regression ===
print("⏳ Entrenando Regresión Logística...")
lr_model = LogisticRegression(multi_class='multinomial', solver='lbfgs', max_iter=1000)
lr_model.fit(X_train, y_train)

# === 9. Evaluar ===
y_pred = lr_model.predict(X_test)

print("\n--- RESULTADOS ---")
print(f"Accuracy: {accuracy_score(y_test, y_pred):.4f}")

# Calcular F1-Score Global
f1_global = f1_score(y_test, y_pred, average='weighted')
print(f"F1-Score Global (Weighted): {f1_global:.4f}")

# Reporte detallado
print("\n--- Reporte de Clasificación ---")
# output_dict=True nos permite usar los datos para graficar después si queremos
report = classification_report(y_test, y_pred, target_names=label_encoder.classes_)
print(report)

# === 10. Guardar modelo ===
joblib.dump(lr_model, "../models/lr_model.save")
print("✅ Logistic Regression guardado en /models/lr_model.save")

# ==========================================
# === 11. GRÁFICOS ===
# ==========================================

# GRÁFICO 1: Matriz de Confusión
plt.figure(figsize=(10, 8))
cm = confusion_matrix(y_test, y_pred)
sns.heatmap(cm, annot=True, fmt='d', cmap='Greens', # Usamos verde para diferenciar del otro modelo
            xticklabels=label_encoder.classes_,
            yticklabels=label_encoder.classes_)
plt.title('Matriz de Confusión - Regresión Logística')
plt.xlabel('Predicción')
plt.ylabel('Realidad')
plt.xticks(rotation=45)
plt.tight_layout()
plt.savefig("../models/lr_confusion_matrix.png")
plt.show()

# GRÁFICO 2: Rendimiento por Clase (F1-Score por clima)
# Extraemos el reporte como diccionario para graficar
report_dict = classification_report(y_test, y_pred, target_names=label_encoder.classes_, output_dict=True)
clases = label_encoder.classes_
f1_scores = [report_dict[cls]['f1-score'] for cls in clases]

plt.figure(figsize=(10, 6))
sns.barplot(x=clases, y=f1_scores, palette="viridis")
plt.title('F1-Score por Tipo de Clima (Regresión Logística)')
plt.ylabel('F1-Score')
plt.xlabel('Clima')
plt.xticks(rotation=45)
plt.ylim(0, 1) # El F1 va de 0 a 1
plt.tight_layout()
plt.savefig("../models/lr_f1_scores.png")
plt.show()

print("✅ Gráficos generados.")