<template>
    <div class="auth-layout-container">
      <router-view v-slot="{ Component }">
        <transition name="fade" mode="out-in">
          <component :is="Component" />
        </transition>
      </router-view>
  
      </div>
  </template>
  
  <script setup>
  // This layout component usually requires minimal script logic.
  // Its primary role is structural (template and styles).
  import { RouterView } from 'vue-router';
  </script>
  
  <style scoped>
  .auth-layout-container {
    display: flex;
    justify-content: center; /* Center horizontally */
    align-items: center;     /* Center vertically */
    min-height: 100vh;       /* Ensure it takes full viewport height */
    /*
     Apply the same background as used in LoginPage/ForgotPasswordPage
     to ensure visual consistency when pages transition.
    */
    background: linear-gradient(to bottom right, #f0f4f8, #d9e2ec);
    padding: 20px; /* Add some padding around the content */
    box-sizing: border-box;
  }
  
  /* Optional: Transition styles for router view */
  .fade-enter-active,
  .fade-leave-active {
    transition: opacity 0.3s ease;
  }
  
  .fade-enter-from,
  .fade-leave-to {
    opacity: 0;
  }
  
  /* Optional: Footer styling if you uncomment the footer HTML */
  /*
  .auth-footer {
    position: absolute;
    bottom: 15px;
    left: 0;
    right: 0;
    text-align: center;
    color: #a0a3a8;
    font-size: 0.85em;
  }
  */
  </style>