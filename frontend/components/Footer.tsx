import Logo from "./Logo";

export default function Footer() {
  return (
    <footer className="mt-16 border-t border-slate-200 bg-white">
      <div className="mx-auto grid max-w-7xl gap-8 px-4 py-10 sm:grid-cols-3">
        <div>
          <Logo />
          <p className="mt-3 max-w-xs text-sm text-slate-500">
            Car parts sold by exact vehicle fitment. Verified compatibility,
            delivery across Kenya, M-Pesa checkout.
          </p>
        </div>
        <div className="text-sm">
          <h3 className="mb-2 font-semibold text-navy">Why buy from us</h3>
          <ul className="space-y-1.5 text-slate-500">
            <li>✓ Fitment verified against your exact car</li>
            <li>✓ Genuine &amp; quality aftermarket brands</li>
            <li>✓ Countrywide delivery</li>
            <li>✓ M-Pesa &amp; card payments</li>
          </ul>
        </div>
        <div className="text-sm">
          <h3 className="mb-2 font-semibold text-navy">Contact</h3>
          <ul className="space-y-1.5 text-slate-500">
            <li>Nairobi, Kenya</li>
            <li>WhatsApp: ask about fitment</li>
          </ul>
        </div>
      </div>
      <div className="border-t border-slate-100 py-4 text-center text-xs text-slate-400">
        © {new Date().getFullYear()} Corporation Premium. All rights reserved.
      </div>
    </footer>
  );
}
