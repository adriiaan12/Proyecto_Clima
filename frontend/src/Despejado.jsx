import React from 'react';
import './Despejado.scss';

const Despejado = () => {
  
  const pajaros = Array.from({ length: 5 });

  return (
    <div className="sunny-container">
      {/* El Sol */}
      <div className="sun"></div>

      {/* Los Pájaros */}
      {pajaros.map((_, index) => (
        <div key={index} className="bird"></div>
      ))}
    </div>
  );
};

export default Despejado;