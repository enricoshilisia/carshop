import Link from "next/link";

import { formatKES, type ProductCard as ProductCardType } from "@/lib/api";

export default function ProductCard({ product }: { product: ProductCardType }) {
  return (
    <Link
      href={product.url}
      className="group flex flex-col rounded-lg border border-slate-200 bg-white p-4 transition-shadow hover:shadow-lg"
    >
      <div className="mb-3 flex h-36 items-center justify-center rounded-md bg-slate-100">
        {product.image ? (
          // eslint-disable-next-line @next/next/no-img-element
          <img
            src={product.image}
            alt={product.name}
            className="max-h-full max-w-full object-contain"
            loading="lazy"
          />
        ) : (
          <svg width="48" height="48" viewBox="0 0 24 24" fill="none" className="text-slate-300" aria-hidden="true">
            <path
              d="M4 17l2-6h12l2 6M6 17h12M7 17v2m10-2v2M8.5 11V8.5A1.5 1.5 0 0110 7h4a1.5 1.5 0 011.5 1.5V11"
              stroke="currentColor"
              strokeWidth="1.5"
              strokeLinecap="round"
              strokeLinejoin="round"
            />
          </svg>
        )}
      </div>
      <span className="text-xs font-semibold uppercase tracking-wide text-amber-700">
        {product.brand}
      </span>
      <span className="mt-1 line-clamp-2 text-sm font-medium text-slate-800 group-hover:text-navy">
        {product.name}
      </span>
      {product.mpn && (
        <span className="mt-0.5 text-xs text-slate-400">MPN: {product.mpn}</span>
      )}
      <div className="mt-auto flex items-baseline justify-between pt-3">
        <span className="text-base font-bold text-navy">
          {formatKES(product.price, product.currency)}
        </span>
        <span
          className={`text-xs font-medium ${product.in_stock ? "text-emerald-600" : "text-slate-400"}`}
        >
          {product.in_stock ? "In stock" : "On order"}
        </span>
      </div>
    </Link>
  );
}
