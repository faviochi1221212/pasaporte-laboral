import react from "@vitejs/plugin-react";
import { defineConfig } from "vite";

// En desarrollo, /api va al backend de FastAPI; en producción FastAPI sirve web/dist.
export default defineConfig({
  plugins: [react()],
  // fs.allow: el ejemplo de modo respaldo se lee de tests/relatos/ (fuera de web/).
  server: { proxy: { "/api": "http://127.0.0.1:8000" }, fs: { allow: [".."] } },
});
