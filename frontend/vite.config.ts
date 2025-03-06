import { sentryVitePlugin } from "@sentry/vite-plugin";
import { defineConfig } from "vite"
import react from "@vitejs/plugin-react"
import path from 'path';

export default defineConfig({
  plugins: [react(), sentryVitePlugin({
    org: "nomana-it",
    project: "liberty-airflow"
  })],
  server: {
    open: true,
    cors: { origin: "*" },
    proxy: {
      '/api': {
        target: "http://localhost:8082",
        changeOrigin: true,
      },
      '/socket.io': {
        target: "ws://localhost:8082",
        changeOrigin: true,
      },
      '/socket': {
        target: "http://localhost:8082",
        changeOrigin: true,
      },     
      '/airflow': {
        target: "http://localhost:8081",
        changeOrigin: true,
      }
  },

  },
  build: {
    outDir: "../backend/app/public/frontend",
    assetsDir: 'assets',
    emptyOutDir: true,
    sourcemap: true
  },
  resolve: {
    alias: {
      // Map '@' to the 'src' directory for absolute imports
     // '@': path.resolve(__dirname, 'src'),
      "@ly_assets": path.resolve(__dirname, 'src/assets'),
      "@ly_app": path.resolve(__dirname, 'src/app'),
      "@ly_components": path.resolve(__dirname, 'src/components'),
      "@ly_styles": path.resolve(__dirname, 'src/styles'),
      "@ly_data": path.resolve(__dirname, 'src/data'),
    },
  },
})