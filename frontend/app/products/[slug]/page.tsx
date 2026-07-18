import type { Metadata } from "next";
import Link from "next/link";
import { notFound } from "next/navigation";

import JsonLd from "@/components/JsonLd";
import { api, ApiError, formatKES, type ProductDetail } from "@/lib/api";

export const revalidate = 3600;

async function load(slug: string): Promise<ProductDetail | null> {
  try {
    return await api.product(slug);
  } catch (err) {
    if (err instanceof ApiError && (err.status === 404 || err.status === 410)) return null;
    throw err;
  }
}

export async function generateMetadata({
  params,
}: {
  params: Promise<{ slug: string }>;
}): Promise<Metadata> {
  const { slug } = await params;
  const data = await load(slug);
  if (!data) return {};
  const p = data.product;
  return {
    title: `${p.brand} ${p.name} | Corporation Premium Kenya`,
    description: p.description?.slice(0, 300),
    alternates: { canonical: p.url },
  };
}

export default async function ProductPage({
  params,
}: {
  params: Promise<{ slug: string }>;
}) {
  const { slug } = await params;
  const data = await load(slug);
  if (!data) notFound();
  const p = data.product;

  return (
    <div>
      <JsonLd data={data.structured_data} />
      <nav className="mb-4 text-xs text-slate-500" aria-label="Breadcrumb">
        <Link href="/" className="hover:underline">Home</Link>
        <span className="mx-1.5 text-slate-300">›</span>
        <span className="font-medium text-slate-700">{p.name}</span>
      </nav>

      <div className="grid gap-8 lg:grid-cols-2">
        {/* Gallery */}
        <div className="flex h-96 items-center justify-center rounded-xl border border-slate-200 bg-white p-6">
          {p.images.length > 0 && p.images[0] ? (
            // eslint-disable-next-line @next/next/no-img-element
            <img src={p.images[0]} alt={p.name} className="max-h-full max-w-full object-contain" />
          ) : (
            <div className="text-center text-slate-300">
              <svg width="90" height="90" viewBox="0 0 24 24" fill="none" className="mx-auto" aria-hidden="true">
                <path
                  d="M4 17l2-6h12l2 6M6 17h12M7 17v2m10-2v2M8.5 11V8.5A1.5 1.5 0 0110 7h4a1.5 1.5 0 011.5 1.5V11"
                  stroke="currentColor" strokeWidth="1.2" strokeLinecap="round" strokeLinejoin="round"
                />
              </svg>
              <span className="text-sm">Photo coming soon</span>
            </div>
          )}
        </div>

        {/* Buy box */}
        <div>
          <span className="text-sm font-semibold uppercase tracking-wide text-amber-700">{p.brand}</span>
          <h1 className="mt-1 text-2xl font-bold text-navy">{p.name}</h1>
          <p className="mt-1 text-sm text-slate-500">
            SKU {p.sku}
            {p.mpn && <> · MPN {p.mpn}</>}
            {" · "}
            <span className="capitalize">{p.condition}</span>
          </p>

          <div className="mt-5 flex items-baseline gap-3">
            <span className="text-3xl font-extrabold text-navy">{formatKES(p.price, p.currency)}</span>
            {p.compare_at && (
              <span className="text-lg text-slate-400 line-through">{formatKES(p.compare_at, p.currency)}</span>
            )}
          </div>
          <p className={`mt-1 text-sm font-medium ${p.in_stock ? "text-emerald-600" : "text-slate-500"}`}>
            {p.in_stock ? "✓ In stock — ships today from Nairobi" : "Available on order"}
          </p>

          <div className="mt-6 flex gap-3">
            <button className="flex-1 rounded-md bg-amber px-6 py-3 font-bold text-navy-900 transition-colors hover:bg-amber-500">
              Add to cart
            </button>
            <a
              href={`https://wa.me/?text=${encodeURIComponent(`Fitment question: ${p.brand} ${p.name} (${p.sku})`)}`}
              className="rounded-md border border-slate-300 px-4 py-3 text-sm font-semibold text-slate-700 transition-colors hover:border-navy hover:text-navy"
            >
              WhatsApp us
            </a>
          </div>

          {p.description && (
            <div className="mt-8">
              <h2 className="mb-2 font-bold text-navy">Description</h2>
              <p className="text-sm leading-relaxed text-slate-600">{p.description}</p>
            </div>
          )}

          {p.part_numbers.length > 0 && (
            <div className="mt-6">
              <h2 className="mb-2 font-bold text-navy">Cross-reference numbers</h2>
              <div className="flex flex-wrap gap-2">
                {p.part_numbers.map((pn) => (
                  <span key={pn.number} className="rounded bg-slate-100 px-2.5 py-1 font-mono text-xs text-slate-600">
                    {pn.number} <span className="uppercase text-slate-400">({pn.kind})</span>
                  </span>
                ))}
              </div>
            </div>
          )}
        </div>
      </div>

      {/* Fitment table */}
      <section className="mt-12">
        <h2 className="mb-3 text-xl font-bold text-navy">
          Fits these vehicles{" "}
          <span className="text-sm font-normal text-slate-400">
            ({p.is_universal ? "universal fit" : `${data.fits_count} vehicle${data.fits_count === 1 ? "" : "s"}`})
          </span>
        </h2>
        {p.is_universal ? (
          <p className="rounded-lg border border-slate-200 bg-white p-5 text-sm text-slate-600">
            Universal part — fits all vehicles. Check the size/spec above against your car before ordering.
          </p>
        ) : data.fits_summary.length > 0 ? (
          <div className="overflow-x-auto rounded-lg border border-slate-200 bg-white">
            <table className="w-full text-sm" data-testid="fitment-table">
              <thead>
                <tr className="border-b border-slate-200 bg-slate-50 text-left text-xs uppercase tracking-wide text-slate-500">
                  <th className="px-4 py-2.5">Vehicle</th>
                  <th className="px-4 py-2.5">Position</th>
                </tr>
              </thead>
              <tbody>
                {data.fits_summary.map((f, i) => (
                  <tr key={i} className="border-b border-slate-100 last:border-0">
                    <td className="px-4 py-2.5 text-slate-700">{f.vehicle}</td>
                    <td className="px-4 py-2.5 capitalize text-slate-500">{f.position || "—"}</td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        ) : (
          <p className="text-sm text-slate-500">Fitment data being verified.</p>
        )}
      </section>

      {/* Also fits — links out to other vehicle storefronts */}
      {data.also_fits.length > 0 && (
        <section className="mt-10">
          <h2 className="mb-3 text-sm font-bold uppercase tracking-wide text-slate-500">
            Shop all parts for these vehicles
          </h2>
          <div className="flex flex-wrap gap-2">
            {data.also_fits.map((l) => (
              <Link
                key={l.path}
                href={l.path}
                className="rounded-full border border-slate-300 bg-white px-4 py-1.5 text-sm text-slate-700 transition-colors hover:border-amber hover:text-navy"
              >
                {l.name}
              </Link>
            ))}
          </div>
        </section>
      )}
    </div>
  );
}
