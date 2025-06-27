import { defineConfig } from 'vite'

export default defineConfig({
    server: {
        host: true, // Esto permite acceder desde dispositivos en la misma red
        port: 3000,
        open: true
    }
}) 