import React from 'react';
import './Nieve.scss';

const Nieve = () => {
  // Creamos 200 copos vacíos
  const copos = Array.from({ length: 200 });

  return (
    <div className="snow">
      {copos.map((_, index) => (
        <div key={index} className="snowflake">
          {/* El span es necesario para rotar el copo independientemente de la caída */}
          <span></span>
        </div>
      ))}
    </div>
  );
};

export default Nieve;