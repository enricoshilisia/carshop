import type { Metadata } from "next";

import Footer from "@/components/Footer";
import GarageBanner from "@/components/GarageBanner";
import Header from "@/components/Header";

import "./globals.css";

export const metadata: Metadata = {
  title: {
    default: "Corporation Premium — Car Parts by Vehicle Fitment, Kenya",
    template: "%s",
  },
  description:
    "Buy car parts that actually fit. Verified fitment for Toyota, Mazda, Nissan and more. Delivery across Kenya, M-Pesa checkout.",
};

export default function RootLayout({ children }: { children: React.ReactNode }) {
  return (
    <html lang="en">
      <body className="flex min-h-screen flex-col">
        <GarageBanner />
        <Header />
        <main className="mx-auto w-full max-w-7xl flex-1 px-4 py-6">{children}</main>
        <Footer />
      </body>
    </html>
  );
}
