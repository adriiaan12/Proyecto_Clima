import React from 'react';
import './Lluvia.scss'; // Importamos los estilos SCSS

const Lluvia = () => {
  // Creamos un array de 500 elementos vacíos para simular el bucle "for"
  const gotas = Array.from({ length: 500 });
  return (
    <div className="rain">
      {/* Elementos decorativos extra que pediste */}
      <div className="left"></div>
      <div className="left center"></div>
      <div className="right center"></div>
      <div className="right"></div>

      {/* Renderizamos las 500 gotas */}
      {gotas.map((_, index) => (
        <div key={index} className="drop"></div>
      ))}
    </div>
  );
};

export default Lluvia;