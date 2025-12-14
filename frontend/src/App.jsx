// En frontend/src/App.jsx
import { useState, useEffect } from 'react'
import axios from 'axios'
import './App.css'

function App() {
  const [data, setData] = useState(null)
  const [ciudad, setCiudad] = useState('Madrid') // Ciudad inicial
  const [fondo, setFondo] = useState('lightblue')

  // Función para pedir datos
  const obtenerClima = (ciudadBusqueda) => {
    // Petición POST enviando la ciudad
    axios.post('http://127.0.0.1:8000/api/', { city: ciudadBusqueda })
      .then(response => {
        setData(response.data);
        actualizarFondo(response.data.clase_clima);
      })
      .catch(error => console.error("Error:", error));
  }

  // Cargar datos al iniciar
  useEffect(() => {
    obtenerClima(ciudad);
  }, []) // Se ejecuta una vez al montar

  const actualizarFondo = (clima) => {
    // Ajusta estas palabras clave según lo que devuelva tu modelo
    if (!clima) return;
    
    if (clima.includes('clouds') || clima.includes('clear')) {
      setFondo('linear-gradient(to bottom, #FFD700, #FFA500)');
    } else if (clima.includes('lluvi') || clima.includes('tormenta')) {
      setFondo('linear-gradient(to bottom, #4b6cb7, #2452b0ff)');
    } else if (clima.includes('nub')) {
      setFondo('linear-gradient(to bottom, #bdc3c7, #095aabff)');
    } else {
      setFondo('#87CEEB'); // Default
    }
  }

  return (
    <div>
      <h1>Predicción Climática</h1>
      
      {/* Selector de ciudades (si tu API devuelve la lista) */}
      <div style={{ marginBottom: '20px' }}>
        <input 
          type="text" 
          value={ciudad} 
          onChange={(e) => setCiudad(e.target.value)}
          placeholder="Escribe una ciudad..."
        />
        <button onClick={() => obtenerClima(ciudad)}>Predecir</button>
      </div>

      {data ? (
        <div style={{ background: 'rgba(0,0,0,0.5)', padding: '20px', borderRadius: '10px' }}>
          <h2>Ciudad: {data.city}</h2>
          <h3>Predicción: {data.prediccion}</h3>
          <p>Temperatura: {data.temperatura}°C</p>
          <p>Humedad: {data.humedad}%</p>
          {data.error && <p style={{color: 'red'}}>{data.error}</p>}
        </div>
      ) : (
        <p>Cargando neuronas...</p>
      )}
    </div>
  )
}

export default App