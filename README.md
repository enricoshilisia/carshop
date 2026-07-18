# Corporation Premium — Vehicle-Fitment Parts Store

Kenya-first car parts store where every part is sold by **exact vehicle fitment**
(make → model → generation → trim → engine → year range). Headless Django owns
the data, fitment resolution, SEO registry and feeds; Next.js only renders.

Built to the spec in [BUILD_PLAN.md](BUILD_PLAN.md) — designed for cPanel shared
hosting (two Passenger apps, MySQL, cron instead of Celery, Cloudflare in front).

```
domain.com          → Node (Passenger)   → Next.js standalone   → frontend/
api.domain.com      → Python (Passenger) → Django + DRF + admin → backend/
```

## Repo layout

| Path | What |
|---|---|
| `backend/` | Django 5.2 + DRF. Apps: `vehicles`, `catalog`, `fitment`, `jobs`, `seo`, `api`, `core` |
| `frontend/` | Next.js 15 (App Router, TS, Tailwind), `output: "standalone"` |
| `infra/` | Build script (Docker), cron reference, deploy scripts |

## Core ideas (see BUILD_PLAN.md for the full rationale)

- **One product row per SKU** — fitment is a relationship (`Fitment`), never duplication.
- **Year ranges with `OPEN_YEAR = 9999`** — never NULL, so overlap tests stay index-friendly.
- **`FitmentIndex`** — pre-computed product↔variant edges; the only table the storefront reads.
- **Exclusion rules** — "fits J150 2009–2023 *except* the 4.0 petrol" is one negative row.
- **`VariantGroup` fingerprints** — variants with identical product sets collapse to ONE
  canonical URL (few strong pages instead of thousands of thin ones).
- **SEO Page Registry** (`SeoPage`) — Django decides index/noindex/canonical/410 per URL;
  Next.js just obeys.
- **Job queue = a table + cron** — no Celery, chunked handlers, dedupe keys, `skip_locked`.
- **JSON-LD generated in Django** and injected verbatim by the frontend.
- **Merchant Center XML feed written to disk** by cron, served statically.

## Local development

### Backend (Django, SQLite by default)

```bash
cd backend
python -m venv .venv && .venv/Scripts/activate    # Windows; use bin/activate on POSIX
pip install -r requirements.txt
cp .env.example .env                              # defaults are fine for dev
python manage.py migrate
python manage.py createcachetable
python manage.py seed_demo                        # Kenya vehicles + demo catalog
python manage.py run_jobs --max-seconds=60        # process queued index rebuilds
python manage.py build_variant_groups
python manage.py rebuild_seo_registry
python manage.py runserver 127.0.0.1:8800
```

Admin: `python manage.py createsuperuser` → http://localhost:8800/admin/

### Frontend (Next.js)

```bash
cd frontend
npm install
npm run dev        # http://localhost:3000  (expects the API on :8800, see .env.local)
```

### Tests

```bash
cd backend  && python manage.py test          # 26 tests: resolver, API contract, feeds
cd frontend && npx playwright test            # 8 E2E tests against both dev servers
```

## Production (cPanel)

1. **Backend**: cPanel "Setup Python App" → `backend/passenger_wsgi.py`; MySQL via
   `.env` (`DB_ENGINE=mysql`); install `mysqlclient`; run `infra/deploy-backend.sh`.
2. **Frontend**: never build on the server. `infra/build.sh` inside
   `node:20-bookworm` Docker → upload `dist.tgz` → extract to a timestamped
   release dir → symlink swap → `touch tmp/restart.txt`.
3. **Cron**: install `infra/crontab.txt`.
4. **Cloudflare**: proxy both hosts; Cache Everything on `/car-parts/*`, `/products/*`,
   `/media/*`; bypass `/api/*` (except media), `/search*`. Zone ID + token in `backend/.env`.
5. Fill in `HOST.md` (Python/Node versions, memory caps, inode limit) before going live.

## Definition of done (from the plan)

Add a product with one fitment rule → it appears on every correct storefront,
in the sitemap (if it clears thresholds), in the GMC feed and in JSON-LD, with
zero manual page work. Change a price → ISR revalidate + Cloudflare purge < 60s.
