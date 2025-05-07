<template>
    <Line :data="chartData" :options="chartOptions" />
  </template>
  
  <script setup>
  import { Line } from 'vue-chartjs'
  import { Chart as ChartJS, Title, Tooltip, Legend, PointElement, LineElement, CategoryScale, LinearScale, Filler } from 'chart.js' // 添加 Filler
  
  ChartJS.register(Title, Tooltip, Legend, PointElement, LineElement, CategoryScale, LinearScale, Filler) // 注册 Filler
  
  defineProps({
    chartData: {
      type: Object,
      required: true
    },
    chartOptions: {
      type: Object,
      default: () => ({
          responsive: true,
          maintainAspectRatio: false,
           plugins: { legend: { display: false } },
           scales: { y: { beginAtZero: true } }
      })
    }
  })
  </script>