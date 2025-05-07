import { createApp } from 'vue'
import App from './App.vue'
import router from './router' // Import router configuration
import { createPinia } from 'pinia' // Import Pinia
import ElementPlus from 'element-plus' // Import Element Plus
import 'element-plus/dist/index.css' // Import Element Plus styles
import * as ElementPlusIconsVue from '@element-plus/icons-vue' // Import Element Plus Icons
import './assets/styles/global.css' // Import global styles (optional)

// Create Vue App Instance
const app = createApp(App)

// Register Element Plus Icons globally
for (const [key, component] of Object.entries(ElementPlusIconsVue)) {
  app.component(key, component)
}

// Use Plugins
app.use(createPinia()) // Use Pinia for state management
app.use(router) // Use Vue Router for navigation
app.use(ElementPlus) // Use Element Plus UI library

// Mount the App
app.mount('#app')