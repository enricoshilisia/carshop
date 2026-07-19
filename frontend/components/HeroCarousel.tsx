"use client";

/**
 * Sliding hero: background car photos crossfade every 6s and the headline
 * rotates with them. Images live in /public/img/hero/ — replace car-1.jpg …
 * car-4.jpg with your own shots (same filenames) and nothing else changes.
 */
import { useEffect, useState } from "react";

import VehicleSelector from "./VehicleSelector";

const SLIDES = [
  {
    src: "/img/hero/car-1.jpg",
    line1: "Parts that fit your car.",
    accent: "Guaranteed.",
    sub: "Every part checked against your exact make, model, generation and year. No guesswork, no wrong orders.",
  },
  {
    src: "/img/hero/car-2.jpg",
    line1: "From brake pads to bodywork.",
    accent: "One search away.",
    sub: "Braking, suspension, filters, electricals and more — for cars, SUVs, pickups, trucks and bodas.",
  },
  {
    src: "/img/hero/car-3.jpg",
    line1: "Genuine parts, delivered.",
    accent: "Pay with M-Pesa.",
    sub: "Same-day delivery in Nairobi, 1–3 days countrywide. OEM and quality aftermarket brands only.",
  },
  {
    src: "/img/hero/car-4.jpg",
    line1: "Know your part number?",
    accent: "Type it. Done.",
    sub: "Search any OEM or aftermarket number — 04465-60280 lands you straight on the right part.",
  },
];

const INTERVAL_MS = 6000;

export default function HeroCarousel() {
  const [active, setActive] = useState(0);

  useEffect(() => {
    const t = setInterval(() => setActive((i) => (i + 1) % SLIDES.length), INTERVAL_MS);
    return () => clearInterval(t);
  }, []);

  return (
    <section className="relative -mx-4 -mt-6 mb-8 overflow-hidden bg-navy-900 text-white">
      {/* Sliding backgrounds */}
      {SLIDES.map((slide, i) => (
        // eslint-disable-next-line @next/next/no-img-element
        <img
          key={slide.src}
          src={slide.src}
          alt=""
          aria-hidden="true"
          className={`absolute inset-0 h-full w-full object-cover transition-all duration-[2000ms] ease-out ${
            i === active ? "scale-105 opacity-100" : "scale-100 opacity-0"
          }`}
        />
      ))}
      {/* Readability overlay */}
      <div className="absolute inset-0 bg-gradient-to-r from-navy-900/95 via-navy-900/80 to-navy-900/40" />
      <div className="absolute inset-0 bg-gradient-to-t from-navy-900/90 via-transparent to-transparent" />

      <div className="relative mx-auto max-w-7xl px-4 pb-10 pt-10 sm:pb-14 sm:pt-12">
        {/* Rotating headline — fixed height so the selector never jumps */}
        <div className="min-h-[150px] max-w-2xl sm:min-h-[170px]">
          {SLIDES.map((slide, i) => (
            <div
              key={slide.src}
              className={`transition-opacity duration-700 ${
                i === active ? "opacity-100" : "pointer-events-none absolute opacity-0"
              }`}
              aria-hidden={i !== active}
            >
              <h1 className="text-3xl font-extrabold leading-tight drop-shadow-sm sm:text-4xl">
                {slide.line1}
                <span className="block text-amber">{slide.accent}</span>
              </h1>
              <p className="mt-3 max-w-xl text-sm text-slate-200 sm:text-base">{slide.sub}</p>
            </div>
          ))}
        </div>

        {/* Slide dots */}
        <div className="mb-4 mt-2 flex gap-2">
          {SLIDES.map((_, i) => (
            <button
              key={i}
              onClick={() => setActive(i)}
              aria-label={`Slide ${i + 1}`}
              className={`h-1.5 rounded-full transition-all ${
                i === active ? "w-6 bg-amber" : "w-3 bg-white/30 hover:bg-white/60"
              }`}
            />
          ))}
        </div>

        <div className="max-w-4xl">
          <VehicleSelector compact />
        </div>
      </div>
    </section>
  );
}
