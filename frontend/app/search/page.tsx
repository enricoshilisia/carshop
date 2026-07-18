import type { Metadata } from "next";
import { redirect } from "next/navigation";

import ProductCard from "@/components/ProductCard";
import VehicleSelector from "@/components/VehicleSelector";
import { api } from "@/lib/api";

export const metadata: Metadata = {
  title: "Search Parts | Corporation Premium Kenya",
  robots: { index: false, follow: true },
};

export const dynamic = "force-dynamic";

export default async function SearchPage({
  searchParams,
}: {
  searchParams: Promise<{ q?: string }>;
}) {
  const { q } = await searchParams;
  const query = (q ?? "").trim();

  if (query) {
    const data = await api.search(query);
    // Part-number or vehicle-intent hit → straight to the right page.
    if (data.redirect_to) redirect(data.redirect_to);

    const results = data.results ?? [];
    return (
      <div>
        <h1 className="mb-1 text-2xl font-bold text-navy">
          Search results for “{query}”
        </h1>
        <p className="mb-6 text-sm text-slate-500">
          {results.length} result{results.length === 1 ? "" : "s"}
        </p>
        {results.length > 0 ? (
          <div className="grid grid-cols-2 gap-4 md:grid-cols-3 xl:grid-cols-4" data-testid="search-results">
            {results.map((p) => (
              <ProductCard key={p.id} product={p} />
            ))}
          </div>
        ) : (
          <div className="max-w-2xl">
            <p className="mb-6 rounded-lg border border-dashed border-slate-300 bg-white p-8 text-center text-slate-500">
              Nothing matched. Try a part number (e.g. <span className="font-mono">04465-60280</span>),
              or find parts by selecting your vehicle below.
            </p>
            <VehicleSelector />
          </div>
        )}
      </div>
    );
  }

  return (
    <div className="max-w-2xl">
      <h1 className="mb-6 text-2xl font-bold text-navy">Search the catalog</h1>
      <VehicleSelector />
    </div>
  );
}
