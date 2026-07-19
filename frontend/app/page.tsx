import Link from "next/link";

import HeroCarousel from "@/components/HeroCarousel";
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
      {/* ================== Hero: sliding car photos + rotating headline ==== */}
      <HeroCarousel />

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

      {/* ====================================== Vehicle-type image tiles ==== */}
      <section className="mb-12">
        <h2 className="mb-4 text-xl font-bold text-navy">Whatever you drive, we cover it</h2>
        <div className="grid grid-cols-2 gap-3 lg:grid-cols-4" data-testid="vehicle-type-tiles">
          {[
            ["/img/tiles/suv.jpg", "SUVs & 4x4s", "Prado, Harrier, X-Trail, CX-5…", "/car-parts/toyota/land-cruiser-prado"],
            ["/img/tiles/pickup.jpg", "Pickups & Trucks", "Hilux, D-Max, Ranger, Canter…", "/car-parts/toyota/hilux"],
            ["/img/tiles/motorcycle.jpg", "Motorcycles", "Boxer, HLX, Ace — boda parts", "/car-parts/bajaj"],
            ["/img/tiles/garage.jpg", "Service Parts", "Filters, oils & full service kits", "/shop/service-kits-lubricants"],
          ].map(([img, title, sub, href]) => (
            <Link
              key={href}
              href={href}
              className="group relative h-44 overflow-hidden rounded-xl sm:h-52"
            >
              {/* eslint-disable-next-line @next/next/no-img-element */}
              <img
                src={img}
                alt={title}
                loading="lazy"
                className="absolute inset-0 h-full w-full object-cover transition-transform duration-500 group-hover:scale-105"
              />
              <div className="absolute inset-0 bg-gradient-to-t from-navy-900/90 via-navy-900/30 to-transparent" />
              <div className="absolute inset-x-0 bottom-0 p-4">
                <p className="font-extrabold text-white drop-shadow">{title}</p>
                <p className="mt-0.5 text-xs text-slate-200">{sub}</p>
                <p className="mt-1.5 text-xs font-semibold text-amber opacity-0 transition-opacity group-hover:opacity-100">
                  Shop now →
                </p>
              </div>
            </Link>
          ))}
        </div>
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
          {[
            {
              href: "/shop/laptops",
              img: "/img/tiles/laptop.jpg",
              title: "Laptops",
              sub: "Dell, HP, Lenovo & MacBook — business-grade machines with warranty.",
              cta: `Shop laptops${laptops?.product_count ? ` (${laptops.product_count})` : ""} →`,
            },
            {
              href: "/shop/phones",
              img: "/img/tiles/phone.jpg",
              title: "Mobile Phones",
              sub: "Samsung, iPhone, Tecno, Infinix & Xiaomi — sealed units, Kenya warranty.",
              cta: `Shop phones${phones?.product_count ? ` (${phones.product_count})` : ""} →`,
            },
          ].map((card) => (
            <Link
              key={card.href}
              href={card.href}
              className="group relative overflow-hidden rounded-xl p-6 text-white transition-shadow hover:shadow-xl"
            >
              {/* eslint-disable-next-line @next/next/no-img-element */}
              <img
                src={card.img}
                alt=""
                aria-hidden="true"
                loading="lazy"
                className="absolute inset-0 h-full w-full object-cover transition-transform duration-500 group-hover:scale-105"
              />
              <div className="absolute inset-0 bg-gradient-to-r from-navy-900/95 via-navy-900/80 to-navy-900/40" />
              <div className="relative">
                <p className="text-xs font-semibold uppercase tracking-wider text-amber">Electronics</p>
                <h3 className="mt-1 text-2xl font-extrabold drop-shadow">{card.title}</h3>
                <p className="mt-1.5 max-w-xs text-sm text-slate-200">{card.sub}</p>
                <span className="mt-4 inline-block rounded-md bg-amber px-4 py-2 text-sm font-bold text-navy-900 transition-colors group-hover:bg-amber-500">
                  {card.cta}
                </span>
              </div>
            </Link>
          ))}
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
