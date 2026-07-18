#!/usr/bin/env bash
# Frontend build — run inside Docker (node:20-bookworm) so the standalone
# node_modules matches the Linux x64 host. NEVER build on the server.
#
#   docker run --rm -v "$PWD":/work -w /work node:20-bookworm bash infra/build.sh
set -euo pipefail
cd "$(dirname "$0")/../frontend"

# NEXT_PUBLIC_* is baked at build time — refuse to ship localhost to production.
if [ -f .env.production ]; then
  grep -q "localhost" .env.production && { echo "ERROR: localhost in .env.production"; exit 1; }
else
  echo "ERROR: frontend/.env.production missing (copy .env.production.example)"; exit 1
fi

rm -rf .next ../dist
npm ci                       # ci, not install — respect the lockfile
npm run build                # next build, output: "standalone"

mkdir -p ../dist
cp -r .next/standalone/. ../dist/
mkdir -p ../dist/.next
cp -r .next/static ../dist/.next/static   # the step everyone forgets
cp -r public ../dist/public 2>/dev/null || true

cd ..
tar -czf dist.tgz -C dist .
echo "artifact: $(du -sh dist.tgz | cut -f1)"
echo "Upload dist.tgz, extract to ~/releases/<timestamp>, symlink-swap, touch tmp/restart.txt"
