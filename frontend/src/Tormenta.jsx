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

    
    const lightning = [];
    let lightTimeCurrent = 0;
    let lightTimeTotal = 50;

    
    const rand = (rMi, rMa) => ~~((Math.random() * (rMa - rMi + 1)) + rMi);
    
    
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

    
    const updateL = () => {
      let i = lightning.length;
      while (i--) {
        let light = lightning[i];
        
        
        light.path.push({
          x: light.path[light.path.length - 1].x + (rand(0, light.xRange) - (light.xRange / 2)),
          y: light.path[light.path.length - 1].y + (rand(0, light.yRange))
        });

        
        if (light.path.length > light.pathLimit) {
          lightning.splice(i, 1);
        }
        light.hasFired = true;
      }
    };

    
    const renderL = () => {
      let i = lightning.length;
      while (i--) {
        let light = lightning[i];


        ctx.strokeStyle = 'hsla(55, 100%, 60%, ' + rand(10, 100) / 100 + ')';
        

        ctx.lineWidth = 1;
        if (rand(0, 30) == 0) ctx.lineWidth = 2;
        if (rand(0, 60) == 0) ctx.lineWidth = 3;

        ctx.beginPath();

        let pathCount = light.path.length;
        ctx.moveTo(light.x, light.y);

        for (let pc = 0; pc < pathCount; pc++) {
          ctx.lineTo(light.path[pc].x, light.path[pc].y);


          if (light.canSpawn) {
            if (rand(0, 100) == 0) {
              light.canSpawn = false;
              createL(light.path[pc].x, light.path[pc].y, false);
            }
          }
        }

        if (!light.hasFired) {

            ctx.fillStyle = 'rgba(255, 255, 255, ' + rand(4, 12) / 100 + ')';
            ctx.fillRect(0, 0, cw, ch);
        }


        if (rand(0, 30) == 0) {
            ctx.fillStyle = 'rgba(255, 255, 255, ' + rand(1, 3) / 100 + ')';
            ctx.fillRect(0, 0, cw, ch);
        }

        ctx.stroke();
      }
    };


    const lightningTimer = () => {
      lightTimeCurrent++;
      if (lightTimeCurrent >= lightTimeTotal) {
        let newX = rand(100, cw - 100);
        let newY = rand(0, ch / 2);
        let createCount = rand(1, 3);
        while (createCount--) {
          createL(newX, newY, true);
        }
        lightTimeCurrent = 0;
        lightTimeTotal = rand(30, 100);
      }
    };

    const clearCanvas = () => {
      ctx.globalCompositeOperation = 'destination-out';
      ctx.fillStyle = 'rgba(0, 0, 0, ' + rand(1, 30) / 100 + ')';
      ctx.fillRect(0, 0, cw, ch);
      ctx.globalCompositeOperation = 'source-over';
    };


    const loop = () => {
      animationFrameId = requestAnimationFrame(loop);
      clearCanvas();
      updateL();
      lightningTimer();
      renderL();
    };


    const handleResize = () => {
      cw = canvas.width = window.innerWidth;
      ch = canvas.height = window.innerHeight;
    };

    window.addEventListener('resize', handleResize);
    loop();


    return () => {
      window.removeEventListener('resize', handleResize);
      cancelAnimationFrame(animationFrameId);
    };
  }, []);

  return <canvas ref={canvasRef} className="storm-canvas" />;
};

export default Tormenta;