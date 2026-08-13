import type { CreateClientConfig } from './api/client.gen';

export const createClientConfig: CreateClientConfig = (config) => ({
  ...config,
  baseUrl: process.env.NEXT_PUBLIC_API_URL || 'http://127.0.0.1:8000',
});