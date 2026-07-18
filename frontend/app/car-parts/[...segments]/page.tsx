import type { Metadata } from "next";
import Link from "next/link";
import { notFound } from "next/navigation";

import StorefrontPage from "@/components/StorefrontPage";
import { api, ApiError, type PageData } from "@/lib/api";

export const revalidate = 3600;

/**
 * One catch-all for the whole /car-parts tree:
 *   1 segment  → models of a make          (taxonomy listing)
 *   2 segments → generations of a model    (taxonomy listing)
 *   3 segments → generation hub            (links to its VariantGroup storefronts)
 *   4+         → SEO page registry lookup  (storefront / vehicle+category template)
 *
 * Django's registry decides everything: 404 when unknown, 410 when empty,
 * directive/canonical for robots. Next.js never decides indexability.
 */

type Params = { segments: string[] };
type Search = { page?: string; brand?: string };

function pathFor(segments: string[]) {
  return `/car-parts/${segments.join("/")}/`;
}

async function loadPage(
  segments: string[],
  search: Search
): Promise<PageData | "gone" | null> {
  try {
    return await api.page(
      pathFor(segments),
      Number(search.page ?? "1"),
      search.brand ?? ""
    );
  } catch (err) {
    if (err instanceof ApiError && err.status === 410) return "gone";
    if (err instanceof ApiError && err.status === 404) return null;
    throw err;
  }
}

export async function generateMetadata({
  params,
  searchParams,
}: {
  params: Promise<Params>;
  searchParams: Promise<Search>;
}): Promise<Metadata> {
  const { segments } = await params;
  const search = await searchParams;
  if (segments.length >= 4) {
    const data = await loadPage(segments, search);
    if (data && data !== "gone") {
      const noindex =
        data.seo.directive !== "index" || Boolean(search.page || search.brand);
      return {
        title: data.seo.title,
        description: data.seo.meta_description,
        alternates: { canonical: data.seo.canonical },
        robots: noindex ? { index: false, follow: true } : { index: true, follow: true },
      };
    }
    return {};
  }
  const label = segments
    .map((s) => s.replace(/-/g, " "))
    .map((s) => s.charAt(0).toUpperCase() + s.slice(1))
    .join(" ");
  return {
    title: `${label} Parts in Kenya | Corporation Premium`,
    robots: { index: false, follow: true },
  };
}

export default async function CarPartsCatchAll({
  params,
  searchParams,
}: {
  params: Promise<Params>;
  searchParams: Promise<Search>;
}) {
  const { segments } = await params;
  const search = await searchParams;

  // Deep paths: the SEO page registry is the source of truth.
  if (segments.length >= 4) {
    const data = await loadPage(segments, search);
    if (data === "gone" || data === null) notFound();
    return (
      <StorefrontPage data={data} basePath={pathFor(segments)} brand={search.brand} />
    );
  }

  // Shallow paths: taxonomy listings.
  if (segments.length === 1) {
    const [make] = segments;
    const models = await api.models(make);
    if (!models.length) notFound();
    return (
      <Listing
        title={`${cap(make)} models`}
        items={models.map((m) => ({ name: m.name, path: `/car-parts/${make}/${m.slug}` }))}
      />
    );
  }

  if (segments.length === 2) {
    const [make, model] = segments;
    const gens = await api.generations(model);
    if (!gens.length) notFound();
    return (
      <Listing
        title={`${cap(make)} ${cap(model)} generations`}
        items={gens.map((g) => ({
          name: `${g.code} (${g.year_display})${g.body_type ? ` · ${g.body_type}` : ""}`,
          path: `/car-parts/${make}/${model}/${g.slug}`,
        }))}
      />
    );
  }

  // Generation hub: one link per VariantGroup storefront.
  const [make, model, gen] = segments;
  const API = process.env.API_URL || process.env.NEXT_PUBLIC_API_URL || "http://localhost:8800";
  const res = await fetch(`${API}/api/v1/vehicles/generations/${gen}/groups/`, {
    next: { revalidate: 3600 },
  });
  const groups: { name: string; years: string; path: string; product_count: number }[] =
    res.ok ? await res.json() : [];
  if (!groups.length) notFound();
  return (
    <Listing
      title={`${cap(make)} ${cap(model)} ${gen.toUpperCase()} — choose your version`}
      items={groups.map((g) => ({
        name: `${g.name} · ${g.years} (${g.product_count} parts)`,
        path: g.path,
      }))}
    />
  );
}

function cap(slug: string) {
  return slug
    .split("-")
    .map((w) => w.charAt(0).toUpperCase() + w.slice(1))
    .join(" ");
}

function Listing({ title, items }: { title: string; items: { name: string; path: string }[] }) {
  return (
    <div>
      <h1 className="mb-6 text-2xl font-bold text-navy">{title}</h1>
      <div className="grid grid-cols-1 gap-3 sm:grid-cols-2 lg:grid-cols-3">
        {items.map((it) => (
          <Link
            key={it.path}
            href={it.path}
            className="rounded-lg border border-slate-200 bg-white px-5 py-4 font-medium text-slate-700 transition-colors hover:border-amber hover:text-navy"
          >
            {it.name}
          </Link>
        ))}
      </div>
    </div>
  );
}
