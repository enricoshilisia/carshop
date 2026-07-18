/** @type {import('next').NextConfig} */
const nextConfig = {
  // Shared hosting: build locally, ship .next/standalone — the server never builds.
  output: "standalone",
  images: {
    // Pillow pre-generates 1200/600/300 WebP. Node must NEVER optimise images
    // on a shared host — that's an OOM waiting for a busy Tuesday.
    unoptimized: true,
  },
};

module.exports = nextConfig;
