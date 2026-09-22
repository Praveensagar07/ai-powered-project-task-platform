import { defineConfig, loadEnv } from 'vite';
import react from '@vitejs/plugin-react';

export default defineConfig(({ mode }) => {
  const env = loadEnv(mode, process.cwd(), '');
  const rawTarget = env.VITE_BACKEND_URL || env.VITE_API_URL || 'http://127.0.0.1:8000';
  const target = rawTarget.replace(/\/api(\/v1)?\/?$/, '');

  return {
    plugins: [react()],
    server: {
      port: 5173,
      proxy: {
        '/api': {
          target,
          changeOrigin: true,
        },
      },
    },
  };
});

