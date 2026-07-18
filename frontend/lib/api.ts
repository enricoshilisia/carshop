/**
 * Single API client. One page = one API call — the frontend never stitches
 * endpoints or computes fitment/SEO itself. Django owns the truth.
 */
const API_URL =
  process.env.API_URL || process.env.NEXT_PUBLIC_API_URL || "http://localhost:8800";

export class ApiError extends Error {
  status: number;
  constructor(status: number, message: string) {
    super(message);
    this.status = status;
  }
}

async function get<T>(
  path: string,
  opts: { revalidate?: number; tags?: string[] } = {}
): Promise<T> {
  const res = await fetch(`${API_URL}${path}`, {
    next: { revalidate: opts.revalidate ?? 3600, tags: opts.tags },
  });
  if (!res.ok) throw new ApiError(res.status, `${res.status} for ${path}`);
  return res.json();
}

export interface Make {
  id: number;
  name: string;
  slug: string;
  logo: string | null;
}
export interface Model {
  id: number;
  name: string;
  slug: string;
  make: string;
}
export interface Generation {
  id: number;
  code: string;
  slug: string;
  year_from: number;
  year_to: number;
  year_display: string;
  body_type: string;
}
export interface Trim {
  id: number;
  name: string;
  slug: string;
}
export interface Engine {
  id: number;
  display: string;
  code: string;
  slug: string;
  fuel: string;
  capacity_cc: number | null;
}

export interface ProductCard {
  id: number;
  slug: string;
  name: string;
  brand: string;
  sku: string;
  mpn: string;
  condition: string;
  url: string;
  image: string | null;
  price: string | null;
  compare_at: string | null;
  currency: string;
  availability: string | null;
  in_stock: boolean;
}

export interface SeoBlock {
  title: string;
  meta_description: string;
  h1: string;
  canonical: string;
  directive: string;
  intro_html: string;
}

export interface PageData {
  kind: string;
  seo: SeoBlock;
  hero?: { vehicle_name: string; years: string; product_count: number };
  breadcrumbs?: { name: string; path: string }[];
  category_tiles?: { name: string; slug: string; count: number; path: string }[];
  products: ProductCard[];
  facets?: { brands: { name: string; slug: string; count: number }[] };
  pagination?: { page: number; page_size: number; total: number; pages: number };
  related_links?: {
    other_trims: { name: string; path: string }[];
    other_generations: { name: string; path: string }[];
    popular_categories: { name: string; path: string }[];
  };
  structured_data?: object[];
}

export interface ProductDetail {
  product: ProductCard & {
    description: string;
    specs: Record<string, unknown>;
    gtin: string;
    category: string;
    category_slug: string;
    is_universal: boolean;
    images: (string | null)[];
    part_numbers: { number: string; kind: string }[];
  };
  fits_summary: { vehicle: string; position: string; years: string }[];
  fits_count: number;
  also_fits: { name: string; path: string }[];
  structured_data: object[];
}

export const api = {
  makes: () => get<Make[]>("/api/v1/vehicles/makes/"),
  models: (make: string) => get<Model[]>(`/api/v1/vehicles/makes/${make}/models/`),
  generations: (model: string) =>
    get<Generation[]>(`/api/v1/vehicles/models/${model}/generations/`),
  trims: (gen: string) => get<Trim[]>(`/api/v1/vehicles/generations/${gen}/trims/`),
  engines: (gen: string) => get<Engine[]>(`/api/v1/vehicles/generations/${gen}/engines/`),
  page: (path: string, page = 1, brand = "") =>
    get<PageData>(
      `/api/v1/page/?path=${encodeURIComponent(path)}${page > 1 ? `&page=${page}` : ""}${
        brand ? `&brand=${encodeURIComponent(brand)}` : ""
      }`
    ),
  product: (slug: string) =>
    get<ProductDetail>(`/api/v1/products/${slug}/`, { tags: [`product-${slug}`] }),
  productFits: (slug: string, page = 1) =>
    get<{ rows: { vehicle: string; position: string }[]; total: number; page: number }>(
      `/api/v1/products/${slug}/fits/?page=${page}`
    ),
  search: (q: string) =>
    get<{ redirect_to?: string; results?: ProductCard[]; query?: string }>(
      `/api/v1/search/?q=${encodeURIComponent(q)}`,
      { revalidate: 0 }
    ),
};

export function formatKES(price: string | null, currency = "KES"): string {
  if (!price) return "";
  const n = Number(price);
  return `${currency} ${n.toLocaleString("en-KE", { maximumFractionDigits: 0 })}`;
}
