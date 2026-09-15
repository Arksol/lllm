import { defineConfig } from "vite";
import react from "@vitejs/plugin-react";

export default defineConfig({
  plugins: [react()],
  // 1420 es el puerto que espera Tauri en desarrollo
  server: { port: 1420, strictPort: true },
  build: { outDir: "dist", target: "es2021", sourcemap: false },
});
