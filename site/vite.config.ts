import path from "node:path"
import tailwindcss from "@tailwindcss/vite"
import react from "@vitejs/plugin-react"
import { defineConfig } from "vite"

// The page is served by ../server.py in production; in dev the API paths go to it too.
const api = ["/health", "/items", "/facets", "/registries", "/blocks", "/captures", "/themes", "/files", "/index.md", "/registries.md"]
const target = process.env.UI_INDEXER_URL ?? "http://127.0.0.1:3040"

export default defineConfig({
  plugins: [react(), tailwindcss()],
  resolve: { alias: { "@": path.resolve(__dirname, "./src") } },
  build: {
    rollupOptions: {
      input: { main: path.resolve(__dirname, "index.html"), docs: path.resolve(__dirname, "docs.html") },
    },
  },
  server: { port: 3042, strictPort: true, host: "127.0.0.1", proxy: Object.fromEntries(api.map((p) => [p, target])) },
})
