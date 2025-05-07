<template>
    <Pie :data="chartData" :options="options" />
  </template>
  
  <script setup>
  import { Pie } from 'vue-chartjs';
  import {
    Chart as ChartJS,
    Title,
    Tooltip,
    Legend,
    ArcElement, // Pie/Doughnut charts require ArcElement
    CategoryScale, // May not be strictly necessary for Pie, but often included
  } from 'chart.js';
  
  // Register the necessary components for Chart.js
  ChartJS.register(Title, Tooltip, Legend, ArcElement, CategoryScale);
  
  // Define the props the component accepts
  defineProps({
    chartData: {
      type: Object,
      required: true,
      // Example structure:
      // {
      //   labels: ['Label 1', 'Label 2', 'Label 3'],
      //   datasets: [{
      //     backgroundColor: ['#41B883', '#E46651', '#00D8FF'],
      //     data: [40, 20, 12]
      //   }]
      // }
    },
    options: {
      type: Object,
      default: () => ({
          responsive: true,
          maintainAspectRatio: false, // Allows chart to resize better in containers
          plugins: { // Optional: configure plugins like legend, tooltips
              legend: {
                  position: 'top', // Example: Position legend at the top
              },
              tooltip: {
                   // Example: Customize tooltips if needed
                   callbacks: {
                       label: function(context) {
                           let label = context.label || '';
                           if (label) {
                               label += ': ';
                           }
                           if (context.parsed !== null) {
                              // Optionally calculate percentage or format value
                              const total = context.dataset.data.reduce((acc, value) => acc + value, 0);
                              const percentage = total > 0 ? ((context.parsed / total) * 100).toFixed(1) + '%' : '0%';
                              label += `${context.formattedValue} (${percentage})`;
                           }
                           return label;
                       }
                   }
              }
          }
      })
    }
  });
  </script>
  
  <style scoped>
  /* Add any specific styles for the chart container if needed */
  </style>