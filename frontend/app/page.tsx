import Link from "next/link";

import VehicleSelector from "@/components/VehicleSelector";
import { api } from "@/lib/api";

export const revalidate = 3600;

export default async function HomePage() {
  const makes = await api.makes();

  return (
    <div>
      {/* Hero */}
      <section className="relative -mx-4 -mt-6 mb-10 bg-navy px-4 pb-16 pt-12 text-white">
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

      {/* Popular makes */}
      <section className="mb-12">
        <h2 className="mb-4 text-xl font-bold text-navy">Shop by make</h2>
        <div className="grid grid-cols-2 gap-3 sm:grid-cols-3 lg:grid-cols-6">
          {makes.map((m) => (
            <Link
              key={m.slug}
              href={`/car-parts/${m.slug}`}
              className="flex items-center justify-center rounded-lg border border-slate-200 bg-white px-4 py-6 text-sm font-semibold text-slate-700 transition-colors hover:border-amber hover:text-navy"
            >
              {m.name}
            </Link>
          ))}
        </div>
      </section>

      {/* Value props */}
      <section className="grid gap-4 sm:grid-cols-3">
        {[
          ["Verified fitment", "Parts are matched to your exact generation, trim, engine and year range — not just the model name."],
          ["Search by part number", "Type any OEM or aftermarket number — 04465-60280 lands you straight on the right part."],
          ["Kenya-wide delivery", "Nairobi same-day, countrywide 1–3 days. Pay on M-Pesa at checkout."],
        ].map(([title, text]) => (
          <div key={title} className="rounded-lg border border-slate-200 bg-white p-5">
            <h3 className="mb-1.5 font-bold text-navy">{title}</h3>
            <p className="text-sm text-slate-500">{text}</p>
          </div>
        ))}
      </section>
    </div>
  );
}
