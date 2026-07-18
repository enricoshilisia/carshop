import Link from "next/link";

import Breadcrumbs from "@/components/Breadcrumbs";
import JsonLd from "@/components/JsonLd";
import ProductCard from "@/components/ProductCard";
import type { PageData } from "@/lib/api";

/** Renders a vehicle storefront / vehicle+category page from ONE /page/ payload. */
export default function StorefrontPage({
  data,
  basePath,
  brand,
}: {
  data: PageData;
  basePath: string;
  brand?: string;
}) {
  const { hero, seo } = data;
  return (
    <div>
      <JsonLd data={data.structured_data} />
      <Breadcrumbs crumbs={data.breadcrumbs ?? []} />

      <div className="mb-6 rounded-xl bg-navy px-6 py-7 text-white">
        <h1 className="text-2xl font-extrabold sm:text-3xl">{seo.h1 || hero?.vehicle_name}</h1>
        {hero && (
          <p className="mt-1.5 text-sm text-slate-300">
            {hero.product_count} part{hero.product_count === 1 ? "" : "s"} with verified fitment
            for the {hero.vehicle_name} ({hero.years.replace("-", "–")})
          </p>
        )}
      </div>

      {data.category_tiles && data.category_tiles.length > 0 && data.kind === "vehicle" && (
        <section className="mb-8">
          <h2 className="mb-3 text-lg font-bold text-navy">Browse by category</h2>
          <div className="flex flex-wrap gap-2">
            {data.category_tiles.map((c) => (
              <Link
                key={c.slug}
                href={c.path}
                className="rounded-full border border-slate-300 bg-white px-4 py-1.5 text-sm font-medium text-slate-700 transition-colors hover:border-amber hover:text-navy"
              >
                {c.name} <span className="text-slate-400">({c.count})</span>
              </Link>
            ))}
          </div>
        </section>
      )}

      <div className="flex flex-col gap-8 lg:flex-row">
        {/* Facet sidebar — plain links so crawlers and no-JS users see them */}
        {data.facets && data.facets.brands.length > 0 && (
          <aside className="lg:w-52 lg:shrink-0">
            <h2 className="mb-2 text-sm font-bold uppercase tracking-wide text-slate-500">
              Brand
            </h2>
            <ul className="space-y-1 text-sm">
              <li>
                <Link
                  href={basePath}
                  className={!brand ? "font-semibold text-navy" : "text-slate-600 hover:text-navy"}
                >
                  All brands
                </Link>
              </li>
              {data.facets.brands.map((b) => (
                <li key={b.slug}>
                  <Link
                    href={`${basePath}?brand=${b.slug}`}
                    className={
                      brand === b.slug ? "font-semibold text-navy" : "text-slate-600 hover:text-navy"
                    }
                  >
                    {b.name} <span className="text-slate-400">({b.count})</span>
                  </Link>
                </li>
              ))}
            </ul>
          </aside>
        )}

        <div className="flex-1">
          {data.products.length === 0 ? (
            <p className="rounded-lg border border-dashed border-slate-300 bg-white p-10 text-center text-slate-500">
              No parts listed yet for this selection — check back soon or{" "}
              <Link href="/search" className="text-navy underline">search the full catalog</Link>.
            </p>
          ) : (
            <div className="grid grid-cols-2 gap-4 md:grid-cols-3 xl:grid-cols-4" data-testid="product-grid">
              {data.products.map((p) => (
                <ProductCard key={p.id} product={p} />
              ))}
            </div>
          )}

          {data.pagination && data.pagination.pages > 1 && (
            <nav className="mt-8 flex justify-center gap-2 text-sm" aria-label="Pagination">
              {Array.from({ length: Math.min(data.pagination.pages, 5) }, (_, i) => i + 1).map(
                (n) => (
                  <Link
                    key={n}
                    href={n === 1 ? basePath : `${basePath}?page=${n}`}
                    className={`rounded-md px-3 py-1.5 ${
                      n === data.pagination!.page
                        ? "bg-navy font-semibold text-white"
                        : "bg-white text-slate-600 ring-1 ring-slate-200 hover:text-navy"
                    }`}
                  >
                    {n}
                  </Link>
                )
              )}
            </nav>
          )}
        </div>
      </div>

      {/* Internal-linking blocks — SEO gold, all server-rendered */}
      {data.related_links && (
        <section className="mt-12 grid gap-8 border-t border-slate-200 pt-8 sm:grid-cols-3">
          {data.related_links.other_trims.length > 0 && (
            <div>
              <h2 className="mb-2 text-sm font-bold uppercase tracking-wide text-slate-500">
                Other trims of this generation
              </h2>
              <ul className="space-y-1 text-sm">
                {data.related_links.other_trims.map((l) => (
                  <li key={l.path}>
                    <Link href={l.path} className="text-navy hover:underline">{l.name}</Link>
                  </li>
                ))}
              </ul>
            </div>
          )}
          {data.related_links.other_generations.length > 0 && (
            <div>
              <h2 className="mb-2 text-sm font-bold uppercase tracking-wide text-slate-500">
                Other generations
              </h2>
              <ul className="space-y-1 text-sm">
                {data.related_links.other_generations.map((l) => (
                  <li key={l.path}>
                    <Link href={l.path} className="text-navy hover:underline">{l.name}</Link>
                  </li>
                ))}
              </ul>
            </div>
          )}
          {data.related_links.popular_categories.length > 0 && (
            <div>
              <h2 className="mb-2 text-sm font-bold uppercase tracking-wide text-slate-500">
                Popular categories for this vehicle
              </h2>
              <ul className="space-y-1 text-sm">
                {data.related_links.popular_categories.map((l) => (
                  <li key={l.path}>
                    <Link href={l.path} className="text-navy hover:underline">{l.name}</Link>
                  </li>
                ))}
              </ul>
            </div>
          )}
        </section>
      )}
    </div>
  );
}
