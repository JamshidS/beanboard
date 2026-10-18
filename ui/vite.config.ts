import { defineConfig } from "vite";
import react from "@vitejs/plugin-react";

export default defineConfig({
  plugins: [react()],
  server: {
    port: 5173,
    proxy: {
      "/api/catalog": "http://localhost:8001",
      "/api/reviews": "http://localhost:8002",
      "/api/insights": "http://localhost:8003",
    },
  },
});
