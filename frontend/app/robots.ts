import type { MetadataRoute } from "next";

export default function robots(): MetadataRoute.Robots {
  return {
    rules: [
      {
        userAgent: "*",
        disallow: ["/search", "/cart", "/checkout", "/*?sort=", "/*?page="],
      },
    ],
  };
}
