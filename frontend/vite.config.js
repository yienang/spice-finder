import { defineConfig } from 'vite'
import react from '@vitejs/plugin-react'

// https://vite.dev/config/
export default defineConfig({
  plugins: [react()],
  server: {
    // Any request the browser makes to a path starting with /api gets
    // transparently forwarded from Vite's dev server (port 5173) to
    // Flask (port 5000). This means your React code can just call
    // fetch('/api/health') — no hardcoded host, no CORS issue during
    // local dev, since as far as the browser's concerned it's all one
    // origin. Flask-Cors (already set up in the backend) is still worth
    // keeping: it covers you if frontend and backend ever end up on
    // genuinely different domains, e.g. after deploying.
    proxy: {
      '/api': 'http://localhost:5000',
    },
  },
})
