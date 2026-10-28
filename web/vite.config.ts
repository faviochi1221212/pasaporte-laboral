import react from "@vitejs/plugin-react";
import { defineConfig } from "vite";

// En desarrollo, /api va al backend de FastAPI; en producción FastAPI sirve web/dist.
export default defineConfig({
  plugins: [react()],
  server: { proxy: { "/api": "http://127.0.0.1:8000" } },
});
