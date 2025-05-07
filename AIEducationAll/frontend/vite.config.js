import { defineConfig } from 'vite'
import vue from '@vitejs/plugin-vue'
import path from 'path' // Import path module

// https://vitejs.dev/config/
export default defineConfig({
  plugins: [vue()],
  resolve: {
    // Path Aliases for cleaner imports
    alias: {
      '@': path.resolve(__dirname, './src'),
    },
  },
  server: {
    port: 5173, // 前端开发服务器端口
    host: '0.0.0.0', // Allow access from network
    // --- ↓↓↓ 添加或修改 proxy 部分 ↓↓↓ ---
    proxy: {
      // 字符串简写写法: http://localhost:5173/api/v1/auth/login -> http://localhost:8000/api/v1/auth/login
      '/api': {
         target: 'http://127.0.0.1:8000', // 您的后端服务器地址
         changeOrigin: true, // 需要虚拟主机站点
         // rewrite: (path) => path.replace(/^\/api/, '') // 如果后端接口路径没有 /api 前缀，取消注释这行
      }
    }
    // --- ↑↑↑ 添加或修改 proxy 部分 ↑↑↑ ---
  },
})