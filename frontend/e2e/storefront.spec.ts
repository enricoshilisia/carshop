import { expect, test } from "@playwright/test";

const API = "http://localhost:8800";

test("home page renders hero, selector and makes", async ({ page }) => {
  await page.goto("/");
  await expect(page).toHaveTitle(/Corporation Premium/);
  await expect(page.getByRole("heading", { name: /Parts that fit your car/i })).toBeVisible();
  await expect(page.getByTestId("vehicle-selector")).toBeVisible();
  await expect(page.getByRole("link", { name: "Toyota", exact: true })).toBeVisible();
});

test("vehicle selector cascade navigates to a storefront", async ({ page }) => {
  await page.goto("/");
  const selector = page.getByTestId("vehicle-selector");
  await selector.getByLabel("Make").selectOption("toyota");
  await selector.getByLabel("Model").selectOption("land-cruiser-prado");
  await selector.getByLabel("Generation").selectOption("j150");
  await selector.getByRole("button", { name: /find parts/i }).click();
  await page.waitForURL(/\/car-parts\/toyota\/land-cruiser-prado\/j150\//);
  await expect(page.getByRole("heading", { level: 1 })).toContainText(/Prado/i);
  await expect(page.getByTestId("product-grid")).toBeVisible();
  // Garage banner appears after choosing a vehicle.
  await expect(page.getByText(/Showing parts for your/i)).toBeVisible();
});

test("storefront page shows products, facets and internal links", async ({ page, request }) => {
  // Ask the API for a live storefront path instead of hardcoding one.
  const res = await request.get(`${API}/api/v1/vehicles/generations/j150/groups/`);
  const groups = await res.json();
  const target = groups.find((g: { product_count: number }) => g.product_count > 0);
  expect(target).toBeTruthy();

  await page.goto(target.path);
  await expect(page.getByTestId("product-grid")).toBeVisible();
  const cards = page.getByTestId("product-grid").locator("a");
  expect(await cards.count()).toBeGreaterThan(0);
  await expect(page.getByRole("heading", { name: /browse by category/i })).toBeVisible();
  // JSON-LD injected from Django, not built in the frontend.
  const jsonld = await page.locator('script[type="application/ld+json"]').first().textContent();
  expect(jsonld).toContain("BreadcrumbList");
});

test("product page renders price, fitment table and cross references", async ({ page }) => {
  await page.goto("/products/brembo-p83-145-front-brake-pads/");
  await expect(page.getByRole("heading", { name: /Brembo P83-145/i })).toBeVisible();
  await expect(page.getByText(/KES\s?14,500/)).toBeVisible();
  await expect(page.getByTestId("fitment-table")).toBeVisible();
  await expect(page.getByText("04465-60280").first()).toBeVisible();
  const jsonld = await page.locator('script[type="application/ld+json"]').first().textContent();
  expect(jsonld).toContain("isAccessoryOrSparePartFor");
});

test("part-number search redirects straight to the product", async ({ page }) => {
  await page.goto("/search?q=04465-60280");
  await page.waitForURL(/\/products\/brembo-p83-145-front-brake-pads\/?$/);
  await expect(page.getByRole("heading", { name: /Brembo P83-145/i })).toBeVisible();
});

test("vehicle-intent search redirects to the storefront", async ({ page }) => {
  await page.goto("/search?q=prado 2018 brake pads");
  await page.waitForURL(/\/car-parts\/toyota\/land-cruiser-prado\//);
});

test("header search box works end to end", async ({ page }) => {
  await page.goto("/");
  await page.getByLabel("Search parts").fill("wiper");
  await page.getByRole("button", { name: "Search" }).click();
  await page.waitForURL(/\/search\?q=wiper/);
  await expect(page.getByTestId("search-results")).toBeVisible();
  await expect(page.getByText(/Denso Hybrid Wiper Blade/i)).toBeVisible();
});

test("taxonomy pages: make and model listings", async ({ page }) => {
  await page.goto("/car-parts/toyota");
  await expect(page.getByRole("heading", { name: /Toyota models/i })).toBeVisible();
  await page.getByRole("link", { name: /Land Cruiser Prado/i }).click();
  await expect(page.getByRole("heading", { name: /generations/i })).toBeVisible();
  await page.getByRole("link", { name: /J150/i }).first().click();
  await expect(page.getByRole("heading", { name: /choose your version/i })).toBeVisible();
});
