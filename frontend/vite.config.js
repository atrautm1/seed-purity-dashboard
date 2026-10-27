import { defineConfig } from 'vite'
import vue from '@vitejs/plugin-vue'
import { fileURLToPath, URL } from 'node:url'
// https://vite.dev
export default defineConfig({
  plugins: [vue()],
  resolve: {
    alias: {
      '@': fileURLToPath(new URL('./src', import.meta.url))
    }
  },
  server: {
    // Crucial for Docker: ensures Vite listens on all network interfaces
    host: '0.0.0.0', 
    port: 5173,
    allowedHosts: true, // <-- Allows any incoming host header (essential behind reverse proxies like Caddy)
    proxy: {
      // Intercepts any request starting with /api and routes it to FastAPI
      '/api': {
        target: 'http://backend:8000', // Uses the Docker Compose service name
        changeOrigin: true,
        // Optional: removes /api from the path before hitting FastAPI
        // e.g., /api/predict becomes /predict on the backend
        // rewrite: (path) => path.replace(/^\/api/, '') 
      }
    }
  }
})