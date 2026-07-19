import Link from "next/link";

import VehicleSelector from "@/components/VehicleSelector";
import { api } from "@/lib/api";

export const revalidate = 3600;

const API = process.env.API_URL || process.env.NEXT_PUBLIC_API_URL || "http://localhost:8800";

interface CategorySummary {
  name: string;
  slug: string;
  kind: string;
  product_count: number;
  children: { name: string; slug: string }[];
}

async function getCategories(): Promise<CategorySummary[]> {
  const res = await fetch(`${API}/api/v1/categories/`, { next: { revalidate: 3600 } });
  return res.ok ? res.json() : [];
}

const POPULAR_SEARCHES = [
  "prado brake pads",
  "harrier shock absorbers",
  "hilux oil filter",
  "fielder spark plugs",
  "cx-5 air filter",
  "04465-60280",
];

export default async function HomePage() {
  const [makes, categories] = await Promise.all([api.makes(), getCategories()]);
  const partCategories = categories
    .filter((c) => c.kind === "vehicle")
    .sort((a, b) => b.product_count - a.product_count);
  const laptops = categories.find((c) => c.slug === "laptops");
  const phones = categories.find((c) => c.slug === "phones");

  return (
    <div>
      {/* ============================================= Hero + vehicle selector */}
      <section className="relative -mx-4 -mt-6 mb-8 bg-navy px-4 pb-14 pt-12 text-white">
        <div className="mx-auto max-w-7xl">
          <div className="max-w-2xl">
            <h1 className="text-3xl font-extrabold leading-tight sm:text-4xl">
              Parts that fit your car.
              <span className="block text-amber">Guaranteed.</span>
            </h1>
            <p className="mt-3 max-w-xl text-slate-300">
              Every part checked against your exact make, model, generation and year.
              No guesswork, no wrong orders, no wasted trips to Kirinyaga Road.
            </p>
          </div>
          <div className="mt-8 max-w-4xl">
            <VehicleSelector compact />
          </div>
        </div>
      </section>

      {/* ======================================================== Trust strip */}
      <section className="mb-10 grid grid-cols-2 gap-3 sm:grid-cols-4">
        {[
          ["Verified fitment", "Matched to generation, trim, engine & year"],
          ["M-Pesa checkout", "Pay the way Kenya pays"],
          ["Countrywide delivery", "Nairobi same-day, upcountry 1–3 days"],
          ["Genuine brands", "OEM & quality aftermarket only"],
        ].map(([title, text]) => (
          <div
            key={title}
            className="rounded-lg border border-slate-200 bg-white px-4 py-3"
          >
            <p className="text-sm font-bold text-navy">✓ {title}</p>
            <p className="mt-0.5 text-xs text-slate-500">{text}</p>
          </div>
        ))}
      </section>

      {/* ======================================================= Shop by make */}
      <section className="mb-12">
        <div className="mb-4 flex items-baseline justify-between">
          <h2 className="text-xl font-bold text-navy">Shop parts by make</h2>
          <Link href="/car-parts" className="text-sm font-medium text-amber-700 hover:underline">
            All makes →
          </Link>
        </div>
        <div className="grid grid-cols-2 gap-3 sm:grid-cols-4 lg:grid-cols-7">
          {makes.slice(0, 14).map((m) => (
            <Link
              key={m.slug}
              href={`/car-parts/${m.slug}`}
              className="flex items-center justify-center rounded-lg border border-slate-200 bg-white px-3 py-5 text-center text-sm font-semibold text-slate-700 transition-colors hover:border-amber hover:text-navy"
            >
              {m.name}
            </Link>
          ))}
        </div>
      </section>

      {/* ================================================= Parts by category */}
      <section className="mb-12">
        <h2 className="mb-1 text-xl font-bold text-navy">Shop parts by category</h2>
        <p className="mb-4 text-sm text-slate-500">
          Braking to bodywork — for cars, pickups, trucks, buses and motorcycles.
        </p>
        <div className="grid grid-cols-2 gap-3 sm:grid-cols-3 lg:grid-cols-4">
          {partCategories.slice(0, 12).map((c) => (
            <Link
              key={c.slug}
              href={`/shop/${c.slug}`}
              className="group rounded-lg border border-slate-200 bg-white p-4 transition-colors hover:border-amber"
            >
              <p className="font-semibold text-slate-800 group-hover:text-navy">{c.name}</p>
              <p className="mt-1 line-clamp-1 text-xs text-slate-400">
                {c.children.slice(0, 3).map((ch) => ch.name).join(" · ") || "Browse all"}
              </p>
              {c.product_count > 0 && (
                <p className="mt-2 text-xs font-medium text-amber-700">
                  {c.product_count} product{c.product_count === 1 ? "" : "s"}
                </p>
              )}
            </Link>
          ))}
        </div>
      </section>

      {/* =================================== Electronics: laptops & phones */}
      <section className="mb-12">
        <h2 className="mb-1 text-xl font-bold text-navy">More than car parts</h2>
        <p className="mb-4 text-sm text-slate-500">
          We also stock genuine laptops and mobile phones — same delivery, same M-Pesa checkout.
        </p>
        <div className="grid gap-4 sm:grid-cols-2">
          <Link
            href="/shop/laptops"
            className="group relative overflow-hidden rounded-xl bg-navy p-6 text-white transition-shadow hover:shadow-xl"
          >
            <p className="text-xs font-semibold uppercase tracking-wider text-amber">Electronics</p>
            <h3 className="mt-1 text-2xl font-extrabold">Laptops</h3>
            <p className="mt-1.5 max-w-xs text-sm text-slate-300">
              Dell, HP, Lenovo & MacBook — business-grade machines with warranty.
            </p>
            <span className="mt-4 inline-block rounded-md bg-amber px-4 py-2 text-sm font-bold text-navy-900 transition-colors group-hover:bg-amber-500">
              Shop laptops{laptops?.product_count ? ` (${laptops.product_count})` : ""} →
            </span>
          </Link>
          <Link
            href="/shop/phones"
            className="group relative overflow-hidden rounded-xl bg-navy-700 p-6 text-white transition-shadow hover:shadow-xl"
          >
            <p className="text-xs font-semibold uppercase tracking-wider text-amber">Electronics</p>
            <h3 className="mt-1 text-2xl font-extrabold">Mobile Phones</h3>
            <p className="mt-1.5 max-w-xs text-sm text-slate-300">
              Samsung, iPhone, Tecno, Infinix & Xiaomi — sealed units, Kenya warranty.
            </p>
            <span className="mt-4 inline-block rounded-md bg-amber px-4 py-2 text-sm font-bold text-navy-900 transition-colors group-hover:bg-amber-500">
              Shop phones{phones?.product_count ? ` (${phones.product_count})` : ""} →
            </span>
          </Link>
        </div>
      </section>

      {/* ======================================================= How it works */}
      <section className="mb-12 rounded-xl border border-slate-200 bg-white p-6">
        <h2 className="mb-5 text-xl font-bold text-navy">How it works</h2>
        <div className="grid gap-6 sm:grid-cols-3">
          {[
            ["1", "Tell us your car", "Pick make, model, generation and year — or just type your part number into search."],
            ["2", "See only what fits", "Every result is verified against your exact vehicle. No compatibility roulette."],
            ["3", "Pay & receive", "M-Pesa or card at checkout. Same-day delivery in Nairobi, 1–3 days countrywide."],
          ].map(([n, title, text]) => (
            <div key={n} className="flex gap-4">
              <span className="flex h-9 w-9 shrink-0 items-center justify-center rounded-full bg-amber font-extrabold text-navy-900">
                {n}
              </span>
              <div>
                <h3 className="font-bold text-navy">{title}</h3>
                <p className="mt-1 text-sm text-slate-500">{text}</p>
              </div>
            </div>
          ))}
        </div>
      </section>

      {/* ==================================================== Popular searches */}
      <section className="mb-4">
        <h2 className="mb-3 text-sm font-bold uppercase tracking-wide text-slate-500">
          Popular searches
        </h2>
        <div className="flex flex-wrap gap-2">
          {POPULAR_SEARCHES.map((q) => (
            <Link
              key={q}
              href={`/search?q=${encodeURIComponent(q)}`}
              className="rounded-full border border-slate-300 bg-white px-4 py-1.5 text-sm text-slate-600 transition-colors hover:border-amber hover:text-navy"
            >
              {q}
            </Link>
          ))}
        </div>
      </section>
    </div>
  );
}
