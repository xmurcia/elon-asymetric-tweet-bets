import { defineConfig } from '@playwright/test';

export default defineConfig({
  testDir: './tests',
  timeout: 30_000,
  retries: process.env.CI ? 2 : 0,
  use: {
    baseURL: process.env.E2E_BASE_URL || 'http://localhost:3000',
    trace: 'on-first-retry',
  },
  webServer: process.env.E2E_NO_WEB_SERVER
    ? undefined
    : {
        command: 'npm start',
        url: 'http://localhost:3000',
        reuseExistingServer: !process.env.CI,
        timeout: 60_000,
      },
});
