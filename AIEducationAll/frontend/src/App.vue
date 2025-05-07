<template>
    <router-view />
  </template>
  
  <script setup>
  // This component usually doesn't need much logic,
  // it mainly acts as a container for the router view.
  // Global concerns like app-wide listeners or modals might be handled here if needed.
  </script>
  
  <style>
  /* You might have some very basic global styles here if needed,
     but prefer using src/assets/styles/global.css */
  #app {
    font-family: Avenir, Helvetica, Arial, sans-serif;
    -webkit-font-smoothing: antialiased;
    -moz-osx-font-smoothing: grayscale;
    color: #2c3e50;
    /* Ensure app takes full height if needed for layouts */
    /* min-height: 100vh; */
  }
  </style>