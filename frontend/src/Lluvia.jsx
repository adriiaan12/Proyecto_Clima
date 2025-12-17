import React from 'react';
import './Lluvia.scss';

const Lluvia = () => {
  
  const gotas = Array.from({ length: 500 });
  return (
    <div className="rain">
      
      <div className="left"></div>
      <div className="left center"></div>
      <div className="right center"></div>
      <div className="right"></div>

      
      {gotas.map((_, index) => (
        <div key={index} className="drop"></div>
      ))}
    </div>
  );
};

export default Lluvia;