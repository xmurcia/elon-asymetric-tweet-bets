import React, { useEffect, useRef } from 'react';
import Chart from 'chart.js/auto';

const GaussChart = () => {
  const chartRef = useRef(null);
  const chartInstance = useRef(null);

  useEffect(() => {
    if (chartInstance.current) {
      chartInstance.current.destroy();
    }

    const ctx = chartRef.current.getContext('2d');
    
    // Gaussian parameters (μ=220, σ=50)
    const mu = 220;
    const sigma = 50;
    const xValues = Array.from({ length: 400 }, (_, i) => i);
    const yValues = xValues.map(x => 
      (1 / (sigma * Math.sqrt(2 * Math.PI))) * Math.exp(-0.5 * ((x - mu) / sigma) ** 2)
    );

    chartInstance.current = new Chart(ctx, {
      type: 'line',
      data: {
        labels: xValues,
        datasets: [{
          label: 'Tweet Frequency Distribution (Gaussian)',
          data: yValues,
          borderColor: 'rgb(75, 192, 192)',
          backgroundColor: 'rgba(75, 192, 192, 0.2)',
          fill: true,
          tension: 0.4,
        }]
      },
      options: {
        responsive: true,
        plugins: {
          legend: {
            position: 'top',
          },
          title: {
            display: true,
            text: 'Asymmetric Strategy: Gaussian Curve (μ=220, σ=50)'
          }
        },
        scales: {
          x: {
            title: {
              display: true,
              text: 'Odds Bucket'
            }
          },
          y: {
            title: {
              display: true,
              text: 'Probability Density'
            }
          }
        }
      }
    });

    return () => {
      if (chartInstance.current) {
        chartInstance.current.destroy();
      }
    };
  }, []);

  return (
    <div style={{ position: 'relative', height: '400px', width: '100%' }}>
      <canvas ref={chartRef} />
    </div>
  );
};

export default GaussChart;