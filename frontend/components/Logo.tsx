import Link from "next/link";

/** Placeholder mark — swap the SVG for the real logo file when it arrives. */
export default function Logo({ light = false }: { light?: boolean }) {
  return (
    <Link href="/" className="flex items-center gap-2.5 shrink-0" aria-label="Corporation Premium — home">
      <svg width="38" height="38" viewBox="0 0 38 38" aria-hidden="true">
        <rect width="38" height="38" rx="8" fill="#E8890C" />
        <text
          x="19"
          y="25"
          textAnchor="middle"
          fontFamily="system-ui, sans-serif"
          fontWeight="800"
          fontSize="16"
          fill="#0F3057"
        >
          CP
        </text>
      </svg>
      <span className="leading-tight">
        <span className={`block font-extrabold text-[15px] tracking-tight ${light ? "text-white" : "text-navy"}`}>
          Corporation Premium
        </span>
        <span className={`block text-[11px] font-medium tracking-wide uppercase ${light ? "text-slate-300" : "text-slate-500"}`}>
          Auto Parts · Kenya
        </span>
      </span>
    </Link>
  );
}
