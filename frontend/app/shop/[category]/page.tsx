import type { Metadata } from "next";
import Link from "next/link";
import { notFound } from "next/navigation";

import ProductCard from "@/components/ProductCard";
import { ApiError, type ProductCard as ProductCardType } from "@/lib/api";

export const revalidate = 3600;

const API = process.env.API_URL || process.env.NEXT_PUBLIC_API_URL || "http://localhost:8800";

interface ShopData {
  category: {
    name: string;
    slug: string;
    kind: string;
    description: string;
    seo_title: string;
    seo_description: string;
  };
  ancestors: { name: string; slug: string }[];
  children: { name: string; slug: string }[];
  products: ProductCardType[];
  pagination: { page: number; page_size: number; total: number; pages: number };
}

async function load(slug: string, page = 1): Promise<ShopData | null> {
  const res = await fetch(`${API}/api/v1/shop/${slug}/${page > 1 ? `?page=${page}` : ""}`, {
    next: { revalidate: 3600 },
  });
  if (res.status === 404) return null;
  if (!res.ok) throw new ApiError(res.status, `shop/${slug}`);
  return res.json();
}

export async function generateMetadata({
  params,
}: {
  params: Promise<{ category: string }>;
}): Promise<Metadata> {
  const { category } = await params;
  const data = await load(category);
  if (!data) return {};
  return {
    title: data.category.seo_title,
    description:
      data.category.seo_description ||
      `Shop ${data.category.name.toLowerCase()} at Corporation Premium Kenya. Genuine products, countrywide delivery, M-Pesa checkout.`,
  };
}

export default async function ShopCategoryPage({
  params,
  searchParams,
}: {
  params: Promise<{ category: string }>;
  searchParams: Promise<{ page?: string }>;
}) {
  const { category } = await params;
  const { page } = await searchParams;
  const data = await load(category, Number(page ?? "1"));
  if (!data) notFound();

  const basePath = `/shop/${data.category.slug}`;
  return (
    <div>
      <nav aria-label="Breadcrumb" className="mb-4 text-xs text-slate-500">
        <Link href="/" className="hover:underline">Home</Link>
        {data.ancestors.map((a) => (
          <span key={a.slug}>
            <span className="mx-1.5 text-slate-300">›</span>
            <Link href={`/shop/${a.slug}`} className="hover:underline">{a.name}</Link>
          </span>
        ))}
        <span className="mx-1.5 text-slate-300">›</span>
        <span className="font-medium text-slate-700">{data.category.name}</span>
      </nav>

      <div className="mb-6 rounded-xl bg-navy px-6 py-7 text-white">
        <h1 className="text-2xl font-extrabold sm:text-3xl">{data.category.name}</h1>
        <p className="mt-1.5 text-sm text-slate-300">
          {data.pagination.total} product{data.pagination.total === 1 ? "" : "s"}
          {data.category.kind === "vehicle" && " — filter by your car for exact fitment"}
        </p>
      </div>

      {data.children.length > 0 && (
        <div className="mb-8 flex flex-wrap gap-2">
          {data.children.map((c) => (
            <Link
              key={c.slug}
              href={`/shop/${c.slug}`}
              className="rounded-full border border-slate-300 bg-white px-4 py-1.5 text-sm font-medium text-slate-700 transition-colors hover:border-amber hover:text-navy"
            >
              {c.name}
            </Link>
          ))}
        </div>
      )}

      {data.products.length === 0 ? (
        <p className="rounded-lg border border-dashed border-slate-300 bg-white p-10 text-center text-slate-500">
          Products coming soon in this category.
        </p>
      ) : (
        <div className="grid grid-cols-2 gap-4 md:grid-cols-3 xl:grid-cols-4" data-testid="shop-grid">
          {data.products.map((p) => (
            <ProductCard key={p.id} product={p} />
          ))}
        </div>
      )}

      {data.pagination.pages > 1 && (
        <nav className="mt-8 flex justify-center gap-2 text-sm" aria-label="Pagination">
          {Array.from({ length: Math.min(data.pagination.pages, 5) }, (_, i) => i + 1).map((n) => (
            <Link
              key={n}
              href={n === 1 ? basePath : `${basePath}?page=${n}`}
              className={`rounded-md px-3 py-1.5 ${
                n === data.pagination.page
                  ? "bg-navy font-semibold text-white"
                  : "bg-white text-slate-600 ring-1 ring-slate-200 hover:text-navy"
              }`}
            >
              {n}
            </Link>
          ))}
        </nav>
      )}
    </div>
  );
}
