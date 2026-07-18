import Link from "next/link";

import VehicleSelector from "@/components/VehicleSelector";

export default function NotFound() {
  return (
    <div className="mx-auto max-w-2xl py-10 text-center">
      <h1 className="text-3xl font-extrabold text-navy">Page not found</h1>
      <p className="mt-2 mb-8 text-slate-500">
        That page doesn&apos;t exist (or no longer stocks parts). Find your vehicle below, or{" "}
        <Link href="/" className="text-navy underline">go home</Link>.
      </p>
      <div className="text-left">
        <VehicleSelector />
      </div>
    </div>
  );
}
