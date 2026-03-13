import { test, expect } from '@playwright/test';

test('landing renders app shell', async ({ page }) => {
  await page.goto('/');

  await expect(
    page.getByText('Elon Asymmetric Tweet Bets', { exact: true })
  ).toBeVisible();

  // RainbowKit connect button should be present.
  await expect(page.getByRole('button', { name: /connect/i })).toBeVisible();
});
