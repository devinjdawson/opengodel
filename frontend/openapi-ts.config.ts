import { defineConfig } from '@hey-api/openapi-ts';

export default defineConfig({
  input: 'http://127.0.0.1:8000/openapi.json',
  output: {
    format: 'prettier',
    path: './src/lib/api',
  },
  plugins: [
    {
      name: '@hey-api/client-next',
      runtimeConfigPath: './src/lib/hey-api-config.ts',
    },
  ],
});