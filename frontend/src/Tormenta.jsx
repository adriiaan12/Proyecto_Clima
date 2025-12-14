import React, { useEffect, useRef } from 'react';
import './Tormenta.scss';

const Tormenta = () => {
  const canvasRef = useRef(null);

  useEffect(() => {
    const canvas = canvasRef.current;
    if (!canvas) return;

    const ctx = canvas.getContext('2d');
    let cw = canvas.width = window.innerWidth;
    let ch = canvas.height = window.innerHeight;
    let animationFrameId;

    // Configuración del Rayo
    const lightning = [];
    let lightTimeCurrent = 0;
    let lightTimeTotal = 50; // Tiempo entre rayos (bájalo para más frecuencia)

    // --- FUNCIONES DE UTILIDAD ---
    const rand = (rMi, rMa) => ~~((Math.random() * (rMa - rMi + 1)) + rMi);
    
    // Crear un nuevo rayo
    const createL = (x, y, canSpawn) => {
      lightning.push({
        x: x,
        y: y,
        xRange: rand(5, 30),
        yRange: rand(5, 25),
        path: [{ x: x, y: y }],
        pathLimit: rand(10, 35),
        canSpawn: canSpawn,
        hasFired: false
      });
    };

    // Actualizar posición del rayo (Lógica matemática de crecimiento)
    const updateL = () => {
      let i = lightning.length;
      while (i--) {
        let light = lightning[i];
        
        // Añadir nuevo segmento al camino
        light.path.push({
          x: light.path[light.path.length - 1].x + (rand(0, light.xRange) - (light.xRange / 2)),
          y: light.path[light.path.length - 1].y + (rand(0, light.yRange))
        });

        // Eliminar rayo si es muy largo
        if (light.path.length > light.pathLimit) {
          lightning.splice(i, 1);
        }
        light.hasFired = true;
      }
    };

    // Dibujar el rayo en el Canvas
    const renderL = () => {
      let i = lightning.length;
      while (i--) {
        let light = lightning[i];

        // COLOR DEL RAYO (Original: hsla(170, ...))
        // Si quieres rayos blancos/azules eléctricos cambia a: 'hsla(220, 100%, 80%, ...)'
        ctx.strokeStyle = 'hsla(55, 100%, 60%, ' + rand(10, 100) / 100 + ')';
        
        // Grosor aleatorio
        ctx.lineWidth = 1;
        if (rand(0, 30) == 0) ctx.lineWidth = 2;
        if (rand(0, 60) == 0) ctx.lineWidth = 3;

        ctx.beginPath();

        let pathCount = light.path.length;
        ctx.moveTo(light.x, light.y);

        for (let pc = 0; pc < pathCount; pc++) {
          ctx.lineTo(light.path[pc].x, light.path[pc].y);

          // Probabilidad de ramificarse (Split)
          if (light.canSpawn) {
            if (rand(0, 100) == 0) {
              light.canSpawn = false;
              createL(light.path[pc].x, light.path[pc].y, false);
            }
          }
        }

        // FLASH DE FONDO
        // Cuando el rayo nace (!hasFired), iluminamos la pantalla
        if (!light.hasFired) {
            // Color del flash (Original: Rojizo rgba(252, 12, 12...))
            // Para flash realista blanco usa: 'rgba(255, 255, 255, ...)'
            ctx.fillStyle = 'rgba(255, 255, 255, ' + rand(4, 12) / 100 + ')';
            ctx.fillRect(0, 0, cw, ch);
        }

        // Flash aleatorio extra
        if (rand(0, 30) == 0) {
            ctx.fillStyle = 'rgba(255, 255, 255, ' + rand(1, 3) / 100 + ')';
            ctx.fillRect(0, 0, cw, ch);
        }

        ctx.stroke();
      }
    };

    // Temporizador para lanzar nuevos rayos
    const lightningTimer = () => {
      lightTimeCurrent++;
      if (lightTimeCurrent >= lightTimeTotal) {
        let newX = rand(100, cw - 100);
        let newY = rand(0, ch / 2); // Nace en la mitad superior
        let createCount = rand(1, 3);
        while (createCount--) {
          createL(newX, newY, true);
        }
        lightTimeCurrent = 0;
        lightTimeTotal = rand(30, 100); // Tiempo aleatorio hasta el siguiente
      }
    };

    // Limpiar pantalla (Efecto fade out)
    const clearCanvas = () => {
      ctx.globalCompositeOperation = 'destination-out';
      // Esto controla qué tan rápido desaparece el rayo (estela)
      ctx.fillStyle = 'rgba(0, 0, 0, ' + rand(1, 30) / 100 + ')';
      ctx.fillRect(0, 0, cw, ch);
      ctx.globalCompositeOperation = 'source-over';
    };

    // Bucle principal de animación
    const loop = () => {
      animationFrameId = requestAnimationFrame(loop);
      clearCanvas();
      updateL();
      lightningTimer();
      renderL();
    };

    // Manejar redimensionado de ventana
    const handleResize = () => {
      cw = canvas.width = window.innerWidth;
      ch = canvas.height = window.innerHeight;
    };

    window.addEventListener('resize', handleResize);
    loop(); // Iniciar animación

    // Cleanup: Limpiar eventos y animación al desmontar (Cambiar de ciudad/clima)
    return () => {
      window.removeEventListener('resize', handleResize);
      cancelAnimationFrame(animationFrameId);
    };
  }, []);

  return <canvas ref={canvasRef} className="storm-canvas" />;
};

export default Tormenta;