import { useState, useEffect } from 'react'
import axios from 'axios'
import './App.css'
import Lluvia from './Lluvia';
import Nieve from './Nieve';
import Nublado from './Nublado';
import Despejado from './Despejado';
import Tormenta from './Tormenta';
import Niebla from './Niebla';
import Bruma from './Bruma';

function App() {
  const [clima, setClima] = useState(null)
  const [fondo, setFondo] = useState('lightblue')
  const [ciudad, setCiudad] = useState('Madrid')

  // Estado para la lista del desplegable
  const [listaCiudades, setListaCiudades] = useState([])
  
  // 1. NUEVO ESTADO: Controla si el menú está abierto o cerrado
  const [isOpen, setIsOpen] = useState(false);

  // Estados climáticos
  const [esLluvioso, setEsLluvioso] = useState(false);
  const [esNieve, setEsNieve] = useState(false);
  const [esNublado, setEsNublado] = useState(false);
  const [esDespejado, setEsDespejado] = useState(false);
  const [esTormenta, setEsTormenta] = useState(false);
  const [esNiebla, setEsNiebla] = useState(false);
  const [esBruma, setEsBruma] = useState(false);

  const obtenerClima = (ciudadBusqueda) => {
    axios.post('http://127.0.0.1:8000/api/', { city: ciudadBusqueda })
      .then(response => {
        const datos = response.data;
        setClima(datos);

        if (datos.available_cities) {
          setListaCiudades(datos.available_cities);
        }

        determinarFondoYClima(datos.clase_clima || datos.prediccion || '');
      })
      .catch(error => console.error("Error cargando el clima:", error));
  }

  useEffect(() => {
    obtenerClima(ciudad);
  }, [])

  const determinarFondoYClima = (condicionRecibida) => {
    if (!condicionRecibida) return;
    const tiempo = condicionRecibida.toLowerCase();

    // Resetear estados
    setEsLluvioso(false); setEsNieve(false); setEsNublado(false);
    setEsDespejado(false); setEsTormenta(false); setEsNiebla(false); setEsBruma(false);

    if (tiempo.includes('clear') || tiempo.includes('sol') || tiempo.includes('despejado')) {
      setEsDespejado(true);
      setFondo('linear-gradient(to bottom, #2980b9, #6dd5fa, #ffffff)');
    } else if (tiempo.includes('thunderstorm') || tiempo.includes('tormenta')) {
      setEsTormenta(true); setEsLluvioso(true);
      setFondo('linear-gradient(to bottom, #0f2027, #203a43, #2c5364)');
    } else if (tiempo.includes('rain') || tiempo.includes('lluvi')) {
      setEsLluvioso(true);
      setFondo('linear-gradient(to bottom, #203a43, #2c5364)');
    } else if (tiempo.includes('snow') || tiempo.includes('niev')) {
      setEsNieve(true);
      setFondo('linear-gradient(to bottom, #E6DADA, #274046)');
    } else if (tiempo.includes('mist') || tiempo.includes('bruma')) {
      setEsBruma(true);
      setFondo('linear-gradient(to bottom, #cfd9df, #e2ebf0)');
    } else if (tiempo.includes('fog') || tiempo.includes('niebla')) {
      setEsNiebla(true);
      setFondo('linear-gradient(to bottom, #3e5151, #decba4)');
    } else if (tiempo.includes('clouds') || tiempo.includes('nub')) {
      setEsNublado(true);
      setFondo('linear-gradient(to bottom, #757F9A, #D7DDE8)');
    } else {
      setFondo('linear-gradient(to bottom, #87CEEB, #E0F7FA)');
    }
  }

  // Manejador básico de cambio (llama a la API)
  const handleCiudadChange = (nuevaCiudad) => {
    setCiudad(nuevaCiudad);
    obtenerClima(nuevaCiudad);
  }

  // 2. FUNCIÓN AUXILIAR: Selecciona la ciudad y CIERRA el menú
  const seleccionarCiudad = (ciudadElegida) => {
    handleCiudadChange(ciudadElegida);
    setIsOpen(false); // Cerramos el menú
  };

  return (
    <div style={{ background: fondo, transition: 'background 1s ease' }}>

      {/* EFECTOS DE FONDO */}
      {esLluvioso && <Lluvia />}
      {esNieve && <Nieve />}
      {esNublado && <Nublado />}
      {esDespejado && <Despejado />}
      {esTormenta && <Tormenta />}
      {esNiebla && <Niebla />}
      {esBruma && <Bruma />}

      {/* CONTENEDOR PRINCIPAL */}
      <div className="main-wrapper">

        {clima ? (
          <div className="glass-card">

            {/* SELECTOR DE CIUDAD (DESPLEGABLE PERSONALIZADO) */}
            <div style={{ marginBottom: '10px' }}>
              <div className="glass-dropdown">
                
                {/* BOTÓN PRINCIPAL: Abre/Cierra al hacer clic */}
                <button 
                    className="glass-select" 
                    onClick={() => setIsOpen(!isOpen)}
                >
                  {ciudad}
                  {/* Flecha dinámica que gira si está abierto */}
                  <span className={`arrow ${isOpen ? 'open' : ''}`}></span>
                </button>

                {/* LISTA DE OPCIONES: Solo se ve si isOpen es true */}
                {isOpen && (
                    <ul className="glass-options">
                    {listaCiudades.map((c, i) => (
                        <li key={i} onClick={() => seleccionarCiudad(c)}>
                        {c}
                        </li>
                    ))}
                    </ul>
                )}
              </div>
            </div>

            {/* DATOS GIGANTES */}
            <div className="temp-huge">{Math.round(clima.temperatura)}°</div>
            <h3 style={{ textTransform: 'capitalize', margin: 0 }}>{clima.prediccion}</h3>

            {/* DETALLES EN REJILLA */}
            <div className="details-grid">
              <div>
                <small>Humedad</small>
                <p style={{ fontSize: '1.5rem', margin: '5px 0' }}>{Math.round(clima.humedad)}%</p>
              </div>
              <div>
                <small>Viento</small>
                {/* Redondeamos a 1 decimal para que quede limpio */}
                <p style={{ fontSize: '1.5rem', margin: '5px 0' }}>
                    {Number(clima.wind_speed).toFixed(1)} km/h
                </p>
              </div>
            </div>

          </div>
        ) : (
          <div className="glass-card">
            <h2>Cargando predicción...</h2>
          </div>
        )}

      </div>
    </div>
  )
}

export default App