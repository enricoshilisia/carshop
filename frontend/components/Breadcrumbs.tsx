import Link from "next/link";

export default function Breadcrumbs({
  crumbs,
}: {
  crumbs: { name: string; path: string }[];
}) {
  if (!crumbs?.length) return null;
  return (
    <nav aria-label="Breadcrumb" className="mb-4 overflow-x-auto whitespace-nowrap text-xs text-slate-500">
      {crumbs.map((c, i) => (
        <span key={c.path}>
          {i > 0 && <span className="mx-1.5 text-slate-300">›</span>}
          {i === crumbs.length - 1 ? (
            <span className="font-medium text-slate-700">{c.name}</span>
          ) : (
            <Link href={c.path} className="hover:text-navy hover:underline">
              {c.name}
            </Link>
          )}
        </span>
      ))}
    </nav>
  );
}
