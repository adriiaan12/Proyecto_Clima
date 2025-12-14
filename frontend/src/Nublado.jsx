import React from 'react';
import './Nublado.scss';

const Nublado = () => {
  // Generamos un array para las nubes
  const nubes = Array.from({ length: 8 });

  return (
    <div className="clouds-container">
      {nubes.map((_, index) => (
        <div key={index} className="cloud"></div>
      ))}
    </div>
  );
};

export default Nublado;