import type { Metadata } from "next";
import Link from "next/link";

import { api } from "@/lib/api";

export const revalidate = 3600;

export const metadata: Metadata = {
  title: "Shop Car Parts by Vehicle | Corporation Premium Kenya",
  description:
    "Choose your car make to browse parts with verified fitment. Toyota, Mazda, Nissan and more.",
};

export default async function CarPartsIndex() {
  const makes = await api.makes();
  return (
    <div>
      <h1 className="mb-2 text-2xl font-bold text-navy">Shop parts by vehicle</h1>
      <p className="mb-6 text-sm text-slate-500">
        Pick your make to drill down to your exact model, generation and year.
      </p>
      <div className="grid grid-cols-2 gap-3 sm:grid-cols-4">
        {makes.map((m) => (
          <Link
            key={m.slug}
            href={`/car-parts/${m.slug}`}
            className="rounded-lg border border-slate-200 bg-white px-4 py-6 text-center font-semibold text-slate-700 transition-colors hover:border-amber hover:text-navy"
          >
            {m.name}
          </Link>
        ))}
      </div>
    </div>
  );
}
