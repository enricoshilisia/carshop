import Link from "next/link";

import Logo from "./Logo";
import SearchBox from "./SearchBox";

export default function Header() {
  return (
    <header className="bg-navy text-white shadow-md">
      <div className="mx-auto flex max-w-7xl flex-col gap-3 px-4 py-3 sm:flex-row sm:items-center sm:gap-6">
        <Logo light />
        <div className="flex-1">
          <SearchBox />
        </div>
        <nav className="flex items-center gap-5 text-sm font-medium text-slate-200">
          <Link href="/car-parts" className="hover:text-amber transition-colors">
            Car Parts
          </Link>
          <Link href="/shop/laptops" className="hover:text-amber transition-colors">
            Laptops
          </Link>
          <Link href="/shop/phones" className="hover:text-amber transition-colors">
            Phones
          </Link>
        </nav>
      </div>
    </header>
  );
}
