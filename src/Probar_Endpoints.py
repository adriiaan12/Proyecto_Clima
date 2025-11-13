import requests

API_KEY = "eyJhbGciOiJIUzI1NiJ9.eyJzdWIiOiJhZHJpYW5zYW5hbDI3QGdtYWlsLmNvbSIsImp0aSI6IjA1MTY0NjAwLTg0NzMtNGNkNC1iZjczLTYyZGEwOWZhMTcyNyIsImlzcyI6IkFFTUVUIiwiaWF0IjoxNzYxMDc5NDk0LCJ1c2VySWQiOiIwNTE2NDYwMC04NDczLTRjZDQtYmY3My02MmRhMDlmYTE3MjciLCJyb2xlIjoiIn0.JwjWB3XH77BfC9Gzt2uGp_o0Ls62wb2WURRCYY7K-BI"
BASE_URL = "https://opendata.aemet.es/opendata/api"

def explorar_api():
    try:
        # Petición al endpoint base
        r = requests.get(BASE_URL, params={"api_key": API_KEY})
        r.raise_for_status()
        data = r.json()
        
        print("Respuesta inicial de la API:")
        print(data)
        
        # Si hay un campo 'datos' con URLs, podemos previsualizar la primera
        if "datos" in data:
            url_datos = data["datos"]
            print(f"\nURL de datos detectada: {url_datos}")
            
            # Previsualización parcial
            r2 = requests.get(url_datos, params={"api_key": API_KEY}, stream=True)
            r2.raise_for_status()
            preview = r2.raw.read(2000).decode('utf-8')  # primeros 2000 caracteres
            print("\n=== Previsualización de los datos ===")
            print(preview)
        else:
            print("\nNo hay campo 'datos' en la respuesta inicial. Tal vez este endpoint solo devuelve información de servicios.")
            
    except requests.exceptions.RequestException as e:
        print(f"Error al conectar con la API: {e}")

explorar_api()
