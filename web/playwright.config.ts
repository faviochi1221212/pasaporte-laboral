import { defineConfig } from "@playwright/test";
import path from "node:path";

const PYTHON = path.resolve("..", ".venv", "Scripts", "python");

// e2e contra el backend en QVAC_MODO=respaldo, que sirve el build de web/dist (correr antes `npm run build`).
export default defineConfig({
  testDir: "../tests/e2e",
  outputDir: "../test-results",
  timeout: 90_000,
  fullyParallel: false,
  workers: 1,
  use: { baseURL: "http://127.0.0.1:8020" },
  projects: [
    { name: "360", use: { viewport: { width: 360, height: 780 }, hasTouch: true, isMobile: true } },
    { name: "1280", use: { viewport: { width: 1280, height: 860 } } },
  ],
  webServer: {
    command: `"${PYTHON}" -m uvicorn app.main:app --port 8020`,
    cwd: "..",
    url: "http://127.0.0.1:8020/api/salud",
    env: { QVAC_MODO: "respaldo" },
    reuseExistingServer: false,
  },
});
