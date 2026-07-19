import { test } from "@playwright/test";

// Not a test suite — a screenshot capture helper. Run with:
//   npx playwright test e2e/screenshots.spec.ts
test("capture UI screenshots", async ({ page }) => {
  await page.setViewportSize({ width: 1360, height: 900 });
  await page.goto("/");
  await page.waitForLoadState("networkidle");
  await page.screenshot({ path: "screenshots/home.png", fullPage: false });
  await page.screenshot({ path: "screenshots/home-full.png", fullPage: true });

  // Mobile viewport — verify the selector layout on a phone
  await page.setViewportSize({ width: 390, height: 844 });
  await page.goto("/");
  await page.waitForLoadState("networkidle");
  await page.screenshot({ path: "screenshots/home-mobile.png", fullPage: false });
  await page.setViewportSize({ width: 1360, height: 900 });

  await page.goto("/car-parts/toyota/land-cruiser-prado/j150/2009-2023/");
  await page.waitForLoadState("networkidle");
  await page.screenshot({ path: "screenshots/storefront.png", fullPage: false });

  await page.goto("/products/brembo-p83-145-front-brake-pads/");
  await page.waitForLoadState("networkidle");
  await page.screenshot({ path: "screenshots/product.png", fullPage: false });
});
