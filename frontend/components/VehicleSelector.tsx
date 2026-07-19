"use client";

/**
 * Make → Model → Generation → Trim → Year cascade. Each step fetches the next
 * options from the API; "Find parts" resolves to the canonical SEO storefront
 * URL and navigates there. The chosen vehicle is remembered in localStorage
 * ("My Garage") — deliberately NOT a cookie, so cached pages never vary by user.
 */
import { useRouter } from "next/navigation";
import { useEffect, useState } from "react";

const API = process.env.NEXT_PUBLIC_API_URL || "http://localhost:8800";

interface Opt {
  slug: string;
  name?: string;
  code?: string;
  display?: string;
  year_from?: number;
  year_to?: number;
  year_display?: string;
}

async function fetchJson(path: string): Promise<Opt[]> {
  const res = await fetch(`${API}${path}`);
  return res.ok ? res.json() : [];
}

export default function VehicleSelector({ compact = false }: { compact?: boolean }) {
  const router = useRouter();
  const [makes, setMakes] = useState<Opt[]>([]);
  const [models, setModels] = useState<Opt[]>([]);
  const [gens, setGens] = useState<Opt[]>([]);
  const [trims, setTrims] = useState<Opt[]>([]);
  const [sel, setSel] = useState({ make: "", model: "", generation: "", trim: "", year: "" });
  const [busy, setBusy] = useState(false);
  const [error, setError] = useState("");

  useEffect(() => {
    fetchJson("/api/v1/vehicles/makes/").then(setMakes);
  }, []);

  const pick = async (field: string, value: string) => {
    const next = { ...sel, [field]: value };
    if (field === "make") next.model = next.generation = next.trim = next.year = "";
    else if (field === "model") next.generation = next.trim = next.year = "";
    else if (field === "generation") next.trim = next.year = "";
    // Commit the selection BEFORE fetching dependent options — on a slow
    // connection the user can hit "Find parts" while the fetch is in flight,
    // and it must see this pick, not the previous state.
    setSel(next);
    setError("");
    if (field === "make") {
      setGens([]);
      setTrims([]);
      setModels(value ? await fetchJson(`/api/v1/vehicles/makes/${value}/models/`) : []);
    } else if (field === "model") {
      setTrims([]);
      setGens(value ? await fetchJson(`/api/v1/vehicles/models/${value}/generations/`) : []);
    } else if (field === "generation") {
      setTrims(value ? await fetchJson(`/api/v1/vehicles/generations/${value}/trims/`) : []);
    }
  };

  const findParts = async () => {
    if (!sel.make || !sel.model) return;
    setBusy(true);
    setError("");
    const params = new URLSearchParams();
    Object.entries(sel).forEach(([k, v]) => v && params.set(k, v));
    const res = await fetch(`${API}/api/v1/vehicles/resolve/?${params}`);
    setBusy(false);
    if (!res.ok) {
      setError("No matching vehicle found — try fewer filters.");
      return;
    }
    const data = await res.json();
    if (data.canonical_url) {
      try {
        localStorage.setItem(
          "garage",
          JSON.stringify({ name: data.display_name, url: data.canonical_url })
        );
        window.dispatchEvent(new Event("garage-changed"));
      } catch {}
      router.push(data.canonical_url);
    } else {
      setError("No parts page for this vehicle yet.");
    }
  };

  // text-base on mobile stops iOS auto-zoom on focus; py-3 gives a 44px touch target.
  const selectCls =
    "w-full rounded-md border border-slate-300 bg-white px-3 py-3 text-base text-slate-800 focus:border-amber focus:outline-none focus:ring-1 focus:ring-amber disabled:bg-slate-100 disabled:text-slate-400 sm:py-2.5 sm:text-sm";

  const gen = gens.find((g) => g.slug === sel.generation);
  const years: number[] = [];
  if (gen?.year_from) {
    const end = gen.year_to === 9999 ? new Date().getFullYear() : gen.year_to!;
    for (let y = end; y >= gen.year_from; y--) years.push(y);
  }

  return (
    <div
      className={`rounded-xl bg-white p-5 shadow-lg ring-1 ring-slate-200 ${compact ? "" : "sm:p-6"}`}
      data-testid="vehicle-selector"
    >
      <h2 className="mb-1 text-lg font-bold text-navy">Find parts for your car</h2>
      <p className="mb-4 text-xs text-slate-500">
        Select your vehicle — we only show parts verified to fit.
      </p>
      {/* 2-up on phones (less scrolling), row of 5 on desktop when compact */}
      <div className={`grid grid-cols-2 gap-2.5 sm:gap-3 ${compact ? "sm:grid-cols-5" : "sm:grid-cols-2"}`}>
        <select aria-label="Make" className={selectCls} value={sel.make} onChange={(e) => pick("make", e.target.value)}>
          <option value="">Make</option>
          {makes.map((m) => (
            <option key={m.slug} value={m.slug}>{m.name}</option>
          ))}
        </select>
        <select aria-label="Model" className={selectCls} value={sel.model} disabled={!sel.make} onChange={(e) => pick("model", e.target.value)}>
          <option value="">Model</option>
          {models.map((m) => (
            <option key={m.slug} value={m.slug}>{m.name}</option>
          ))}
        </select>
        <select aria-label="Generation" className={selectCls} value={sel.generation} disabled={!sel.model} onChange={(e) => pick("generation", e.target.value)}>
          <option value="">Generation</option>
          {gens.map((g) => (
            <option key={g.slug} value={g.slug}>{g.code} ({g.year_display})</option>
          ))}
        </select>
        <select aria-label="Trim" className={selectCls} value={sel.trim} disabled={!sel.generation} onChange={(e) => pick("trim", e.target.value)}>
          <option value="">Trim (optional)</option>
          {trims.map((t) => (
            <option key={t.slug} value={t.slug}>{t.name}</option>
          ))}
        </select>
        <select aria-label="Year" className={selectCls} value={sel.year} disabled={!sel.generation} onChange={(e) => setSel({ ...sel, year: e.target.value })}>
          <option value="">Year (optional)</option>
          {years.map((y) => (
            <option key={y} value={y}>{y}</option>
          ))}
        </select>
        <button
          onClick={findParts}
          disabled={!sel.model || busy}
          className={`col-span-2 rounded-md bg-amber px-5 py-3 text-base font-bold text-navy-900 transition-colors hover:bg-amber-500 disabled:cursor-not-allowed disabled:bg-slate-200 disabled:text-slate-400 sm:py-2.5 sm:text-sm ${compact ? "sm:col-span-1" : "sm:col-span-2"}`}
        >
          {busy ? "Finding…" : "Find parts"}
        </button>
      </div>
      {error && <p className="mt-3 text-sm text-red-600">{error}</p>}
    </div>
  );
}
