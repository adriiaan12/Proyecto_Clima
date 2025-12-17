import React from 'react';
import './Nieve.scss';

const Nieve = () => {
  
  const copos = Array.from({ length: 200 });

  return (
    <div className="snow">
      {copos.map((_, index) => (
        <div key={index} className="snowflake">
          
          <span></span>
        </div>
      ))}
    </div>
  );
};

export default Nieve;