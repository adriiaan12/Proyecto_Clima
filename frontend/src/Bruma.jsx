import React from 'react';
import './Bruma.scss';

const Bruma = () => {
  // Generamos un array para los parches de bruma
  const parches = Array.from({ length: 6 });

  return (
    <div className="mist-container">
      {parches.map((_, index) => (
        <div key={index} className="mist-patch"></div>
      ))}
    </div>
  );
};

export default Bruma;