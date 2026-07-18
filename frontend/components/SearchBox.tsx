"use client";

import { useRouter } from "next/navigation";
import { useState } from "react";

export default function SearchBox() {
  const router = useRouter();
  const [q, setQ] = useState("");

  return (
    <form
      role="search"
      className="flex w-full max-w-xl"
      onSubmit={(e) => {
        e.preventDefault();
        if (q.trim()) router.push(`/search?q=${encodeURIComponent(q.trim())}`);
      }}
    >
      <input
        type="search"
        value={q}
        onChange={(e) => setQ(e.target.value)}
        placeholder="Search part number, e.g. 04465-60280, or “prado 2018 brake pads”"
        className="w-full rounded-l-md border-0 px-4 py-2.5 text-sm text-slate-800 placeholder:text-slate-400 focus:outline-none focus:ring-2 focus:ring-amber"
        aria-label="Search parts"
      />
      <button
        type="submit"
        className="rounded-r-md bg-amber px-5 text-sm font-semibold text-navy-900 hover:bg-amber-500 transition-colors"
      >
        Search
      </button>
    </form>
  );
}
