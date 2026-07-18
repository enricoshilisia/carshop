"use client";

/**
 * "Showing parts for your Toyota Prado TX 2018 — Change". Reads localStorage
 * client-side only, so cached/ISR pages never vary per user (the classic
 * garage-cookie cache-poisoning bug is structurally impossible here).
 */
import Link from "next/link";
import { useEffect, useState } from "react";

export default function GarageBanner() {
  const [garage, setGarage] = useState<{ name: string; url: string } | null>(null);

  useEffect(() => {
    const read = () => {
      try {
        const raw = localStorage.getItem("garage");
        setGarage(raw ? JSON.parse(raw) : null);
      } catch {}
    };
    read();
    // Re-read when the selector saves a vehicle (same tab) or another tab does.
    window.addEventListener("garage-changed", read);
    window.addEventListener("storage", read);
    return () => {
      window.removeEventListener("garage-changed", read);
      window.removeEventListener("storage", read);
    };
  }, []);

  if (!garage) return null;
  return (
    <div className="sticky top-0 z-40 border-b border-amber-500/30 bg-navy-900 px-4 py-2 text-center text-xs text-white sm:text-sm">
      <span className="text-emerald-400">✓</span> Showing parts for your{" "}
      <Link href={garage.url} className="font-semibold text-amber underline-offset-2 hover:underline">
        {garage.name}
      </Link>
      <button
        className="ml-3 text-slate-300 underline underline-offset-2 hover:text-white"
        onClick={() => {
          localStorage.removeItem("garage");
          setGarage(null);
        }}
      >
        Change
      </button>
    </div>
  );
}
