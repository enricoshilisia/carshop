# BUILD_PLAN.md — Vehicle-Fitment Parts Store (Pure Django, Shared Hosting)

> **How to use:** paste into Claude Code as the working spec. Build phase by phase.
> Phases 1–2 are the product. Everything else is decoration on top of them.

---

## 0. Constraints this plan is designed around

**Target: cPanel-style shared hosting.** That means, concretely:

| No | Yes |
|---|---|
| No Redis | Django DB cache table |
| No Celery / no worker process | Cron + a DB job table |
| No `next build` on the server | Build locally in Docker, ship one tarball (§9) |
| No Docker | Passenger / `passenger_wsgi.py` + virtualenv |
| No long-running processes | Everything finishes inside one request or one cron tick |
| No Postgres extensions (maybe no Postgres at all) | MySQL 8 / MariaDB 10.6+ compatible schema |
| No Meilisearch / Typesense | MySQL `FULLTEXT` + exact part-number index |
| No Vercel ISR infra | Next.js **standalone** + filesystem ISR cache + Cloudflare |

**Two Passenger apps on one account.** Next.js stays — the host runs Node via cPanel's *Setup
Node.js App*. So:

```
domain.com          → Node (Passenger)   → Next.js standalone server   → frontend
api.domain.com      → Python (Passenger) → Django + DRF + /admin       → data + truth
```

The two apps are separate cPanel applications on the same account, sharing a MySQL database and a
`/media` directory. Django is headless: it owns fitment, the SEO registry, and the admin. Next.js
owns nothing but rendering.

**Three rules make this work on shared hosting** — break any one and the account gets suspended:

1. **Never run `next build` on the server.** It will eat every CPU-second and MB of RAM the host
   allows and get killed halfway. Build in GitHub Actions (or locally), `output: "standalone"`,
   rsync/upload `.next/standalone` + `.next/static` + `public`. The server only ever runs
   `node server.js`. This is the single most important line in this document.
2. **Budget the memory.** Node idles at ~150–250MB, Python at ~80–120MB. If your plan caps total
   memory at 1GB and `nproc` at 20, you are fine; at 512MB you are not, and the Node app will get
   OOM-killed under crawl. Check `HOST.md` before writing a line of code.
3. **ISR writes to disk.** `.next/cache/fetch-cache` and the ISR page cache generate thousands of
   small files. **Watch the inode count, not the disk quota** — that's what kills cPanel accounts.
   Cap `generateStaticParams` (see Phase 5) and let Cloudflare, not the filesystem, be the real cache.

**Cloudflare is not optional here — it is the missing infrastructure.** Free tier, Cache Everything
rule, purge-by-URL API. It replaces Redis, does most of the job ISR would do on Vercel, gives free
HTTPS, and cuts origin CPU by ~90% on SEO pages because Googlebot and repeat visitors never reach
Node at all. With Cloudflare in front, your ISR cache is a second-line defence, not the front line.
Set this up in Phase 0, not later.

**The honest caveat, stated once:** shared hosting will hold up to roughly 20–30k SKUs with
Cloudflare in front. Past that — mainly the nightly rebuild and the Merchant sync — you will hit
CPU-second and process limits, and a ~$6/month VPS removes every constraint in this table. The
plan below is built so that migration is a deploy, not a rewrite: no host-specific code, no
proprietary APIs, plain Django. Build here, move when the numbers force it.

---

## 1. What we are building

A parts store (Kenya-first) whose flagship vertical is **car parts sold by vehicle fitment**, plus
non-fitment categories (laptops, phones, accessories).

| Surface | URL shape | Target |
|---|---|---|
| **Vehicle storefront** | `/car-parts/toyota/land-cruiser-prado/j150/tx/2018-2023/` | "prado tx parts kenya" |
| **Vehicle + category** | `/car-parts/toyota/land-cruiser-prado/j150/tx/2018-2023/brake-pads/` | long-tail |
| **Product** | `/products/brembo-p83-145-front-brake-pads/` | Google Shopping / free listings |
| **General category** | `/laptops/dell/latitude/` | non-vehicle catalog |

**One template per surface. Thousands of pages. Zero manual page creation.**

### Non-negotiable principles

1. **One product row per SKU.** Never duplicate a brake pad per car. Fitment is a relationship.
2. **Year ranges, not year rows.** Fitment is `(generation, trim, engine, year_from, year_to)`.
3. **Not every URL deserves Google.** An SEO Page Registry decides index / noindex / canonical.
4. **Merchant Center is designed in from day one**, not bolted on later.
5. **Reads are pre-computed.** Shared hosting cannot afford clever queries at request time.

---

## 2. Stack

```
— BACKEND (api.domain.com) ————————————————————————
Python       3.11+ (whatever cPanel offers — check before you start)
Django       5.x + Django REST Framework
Database     MySQL 8 / MariaDB 10.6+  (Postgres works too; schema below is portable)
Cache        Django DatabaseCache  (manage.py createcachetable)
Sessions     cached_db  (admin only — the storefront is stateless)
Queue        Job model + cron        (see §4)
Search       MySQL FULLTEXT + PartNumber exact index
Images       Pillow, resized on upload, served from /media via Cloudflare
Payments     M-Pesa Daraja STK Push
Feeds        Google Merchant XML feed written to disk by cron; Merchant API later
Deploy       Git pull + passenger_wsgi.py + cPanel "Setup Python App"

— FRONTEND (domain.com) —————————————————————————
Node         20 LTS via cPanel "Setup Node.js App" (Passenger)
Next.js      15, App Router, output: "standalone", server components + ISR
TypeScript, Tailwind (compiled at build time, in CI — never on the server)
Data         fetch() → DRF, with next: { revalidate, tags }
Deploy       CI builds → rsync .next/standalone + .next/static + public → restart app

— SHARED ————————————————————————————————————————
Edge         Cloudflare free tier — Cache Everything + purge API (in front of BOTH)
```

**Dependencies (keep this list short — shared hosting hates compilation):**
```
Django, djangorestframework, mysqlclient (or psycopg[binary]), Pillow, whitenoise,
requests, python-decouple, django-treebeard, openpyxl
```
No numpy, no pandas, no lxml. If a package needs a C compiler, find another package.

**npm side:** `next`, `react`, `react-dom`, `tailwindcss`, `clsx`. That's the list. Every extra
client dependency is bundle weight on a Safaricom 4G connection and RAM in a Passenger process you
do not have to spare. No component libraries, no state managers, no chart libs.

---

## 3. The fitment data model (Phase 1 — build this FIRST)

### 3.1 Vehicle taxonomy

```
VehicleMake        Toyota
  └── VehicleModel        Land Cruiser Prado
        └── VehicleGeneration   J150 (2009–2023)
              ├── VehicleTrim         TX / TX-L / VX
              └── VehicleEngine       2.8L Diesel · 1GD-FTV
                    └── VehicleVariant   ← the atomic, sellable-against unit
```

`VehicleVariant` is the **canonical fitment target**. Everything above it is navigation.

```python
# apps/vehicles/models.py
OPEN_YEAR = 9999   # sentinel for "still in production" — NEVER use NULL for year_to.
                   # NULL forces OR-clauses that MySQL will not index. This one choice
                   # is the difference between a 3ms and a 300ms storefront query.

class VehicleMake(models.Model):
    name       = models.CharField(max_length=80, unique=True)     # Toyota
    slug       = models.SlugField(unique=True)                    # toyota
    logo       = models.ImageField(upload_to="makes/", blank=True)
    popularity = models.PositiveIntegerField(default=0, db_index=True)
    is_active  = models.BooleanField(default=True)

class VehicleModel(models.Model):
    make = models.ForeignKey(VehicleMake, on_delete=models.PROTECT, related_name="models")
    name = models.CharField(max_length=120)                       # Land Cruiser Prado
    slug = models.SlugField()                                     # land-cruiser-prado
    class Meta:
        unique_together = [("make", "slug")]

class VehicleModelAlias(models.Model):
    """No ArrayField on MySQL. Aliases power search + old-URL redirects."""
    model = models.ForeignKey(VehicleModel, on_delete=models.CASCADE, related_name="aliases")
    alias = models.CharField(max_length=120, db_index=True)       # "Prado", "LC Prado"

class VehicleGeneration(models.Model):
    model     = models.ForeignKey(VehicleModel, on_delete=models.PROTECT, related_name="generations")
    code      = models.CharField(max_length=40)                   # J150
    slug      = models.SlugField()                                # j150
    year_from = models.PositiveSmallIntegerField()                # 2009
    year_to   = models.PositiveSmallIntegerField(default=OPEN_YEAR)
    body_type = models.CharField(max_length=40, blank=True)       # SUV / Sedan / Pickup
    facelift  = models.CharField(max_length=40, blank=True)
    image     = models.ImageField(upload_to="generations/", blank=True)
    class Meta:
        unique_together = [("model", "slug")]

class VehicleTrim(models.Model):
    generation = models.ForeignKey(VehicleGeneration, on_delete=models.PROTECT, related_name="trims")
    name, slug = ...                                              # TX / tx
    class Meta:
        unique_together = [("generation", "slug")]

class VehicleEngine(models.Model):
    generation  = models.ForeignKey(VehicleGeneration, on_delete=models.PROTECT, related_name="engines")
    display     = models.CharField(max_length=80)                 # 2.8L Diesel
    code        = models.CharField(max_length=40, blank=True)     # 1GD-FTV
    slug        = models.SlugField()                              # 2-8-diesel-1gd-ftv
    fuel        = models.CharField(max_length=16, choices=FUEL)
    capacity_cc = models.PositiveIntegerField(null=True)
    class Meta:
        unique_together = [("generation", "slug")]

class VehicleVariant(models.Model):
    """The atomic vehicle. A part fits (or does not fit) THIS."""
    generation   = models.ForeignKey(VehicleGeneration, on_delete=models.CASCADE, related_name="variants")
    trim         = models.ForeignKey(VehicleTrim, null=True, blank=True, on_delete=models.CASCADE)
    engine       = models.ForeignKey(VehicleEngine, null=True, blank=True, on_delete=models.CASCADE)
    drivetrain   = models.CharField(max_length=8, blank=True)     # "" = any
    transmission = models.CharField(max_length=16, blank=True)
    year_from    = models.PositiveSmallIntegerField()
    year_to      = models.PositiveSmallIntegerField(default=OPEN_YEAR)
    market       = models.CharField(max_length=8, default="KE")   # KE / JP-import / EU
    is_active    = models.BooleanField(default=True)
    class Meta:
        indexes = [models.Index(fields=["generation", "year_from", "year_to"])]
        constraints = [models.CheckConstraint(check=Q(year_to__gte=F("year_from")),
                                              name="variant_year_order")]
```

**Overlap test, portable and index-friendly (no Postgres ranges):**
```python
# does fitment [a1,a2] overlap variant [b1,b2]?   a1 <= b2 AND b1 <= a2
qs.filter(year_from__lte=f.year_to, year_to__gte=f.year_from)
```

**Kenya reality — plate lookup (Phase 8, model it now):**
```python
class VehicleRegistrationLookup(models.Model):
    """Kenyans search by KDA 123A, not by trim. Cache every resolution forever."""
    plate       = models.CharField(max_length=16, db_index=True)
    vin         = models.CharField(max_length=32, blank=True, db_index=True)
    variant     = models.ForeignKey(VehicleVariant, null=True, on_delete=models.SET_NULL)
    raw_payload = models.JSONField(default=dict)
    confidence  = models.FloatField(default=0)
    resolved_at = models.DateTimeField(auto_now=True)
```

### 3.2 Catalog

```python
class Brand(models.Model):            # Brembo, Bosch, Denso, Toyota Genuine, Dell
    name, slug, logo = ...
    is_oem = models.BooleanField(default=False)

class Category(MP_Node):              # django-treebeard, materialized path — cheap on MySQL
    name = models.CharField(max_length=120)                    # Brake Pads
    slug = models.SlugField(db_index=True)                     # brake-pads
    kind = models.CharField(choices=[("vehicle","Vehicle part"),("general","General")])
    google_category = models.CharField(max_length=255, blank=True)   # GPC path
    icon, description, seo_title, seo_description = ...

class Product(models.Model):
    sku          = models.CharField(max_length=64, unique=True)
    mpn          = models.CharField(max_length=64, blank=True, db_index=True)   # P83-145
    gtin         = models.CharField(max_length=14, blank=True, db_index=True)
    brand        = models.ForeignKey(Brand, on_delete=models.PROTECT)
    category     = models.ForeignKey(Category, on_delete=models.PROTECT)
    name         = models.CharField(max_length=255)
    slug         = models.SlugField(max_length=280, unique=True)
    description  = models.TextField(blank=True)
    specs        = models.JSONField(default=dict)   # {"position":"front","width_mm":155}
    condition    = models.CharField(choices=[("new","New"),("used","Used"),("refurbished","Refurbished")])
    weight_kg    = models.DecimalField(max_digits=7, decimal_places=3, default=0)
    is_universal = models.BooleanField(default=False)   # fits every vehicle
    is_active    = models.BooleanField(default=True, db_index=True)

class ProductImage(models.Model):
    product = models.ForeignKey(Product, on_delete=models.CASCADE, related_name="images")
    image, alt, sort_order, is_primary = ...
    # on save(): generate 1200/600/300 WebP derivatives with Pillow. Never resize at request time.

class Offer(models.Model):
    """Price + stock live here, separate from Product, so multi-seller is a later flag not a rewrite."""
    product      = models.OneToOneField(Product, on_delete=models.CASCADE, related_name="offer")
    price        = models.DecimalField(max_digits=12, decimal_places=2)     # KES
    compare_at   = models.DecimalField(max_digits=12, decimal_places=2, null=True)
    currency     = models.CharField(max_length=3, default="KES")
    stock_qty    = models.IntegerField(default=0)
    availability = models.CharField(choices=AVAILABILITY, db_index=True)
    lead_time_days = models.PositiveSmallIntegerField(default=0)
```
> `OneToOneField` now, `ForeignKey` when you add sellers. One migration, no redesign.

### 3.3 Fitment — the core table

```python
class Fitment(models.Model):
    """
    One row = 'this product fits this vehicle line, these years, this position'.
    Authored at GENERATION level with optional trim/engine narrowing. NEVER per-year.
    """
    product      = models.ForeignKey(Product, on_delete=models.CASCADE, related_name="fitments")
    generation   = models.ForeignKey(VehicleGeneration, on_delete=models.CASCADE)
    trim         = models.ForeignKey(VehicleTrim, null=True, blank=True, on_delete=models.CASCADE)
    engine       = models.ForeignKey(VehicleEngine, null=True, blank=True, on_delete=models.CASCADE)
    drivetrain   = models.CharField(max_length=8, blank=True)     # "" = any
    year_from    = models.PositiveSmallIntegerField()
    year_to      = models.PositiveSmallIntegerField(default=OPEN_YEAR)
    position     = models.CharField(max_length=24, blank=True)     # front / rear / left / right
    notes        = models.CharField(max_length=255, blank=True)    # "Not for vehicles with ADAS"
    is_exclusion = models.BooleanField(default=False)              # NEGATIVE rule
    source       = models.CharField(max_length=32, default="manual")   # manual/supplier/tecdoc
    confidence   = models.FloatField(default=1.0)
    verified_by  = models.ForeignKey(User, null=True, on_delete=models.SET_NULL)
    class Meta:
        indexes = [models.Index(fields=["generation", "year_from", "year_to"]),
                   models.Index(fields=["product"])]
```

> **`is_exclusion` is the field everyone forgets.** Real catalogs need "fits J150 2015–2023
> **except** the 1KD engine". Without it you hand-author a dozen narrow positive rows and get one
> of them wrong. Exclusions are subtracted after inclusion.

### 3.4 The resolved index — pre-computed reads

```python
class FitmentIndex(models.Model):
    """
    Flattened product ↔ variant edges. This is the ONLY table the storefront reads.
    On shared hosting you cannot afford range math at request time. You afford one index seek.
    """
    product  = models.ForeignKey(Product, on_delete=models.CASCADE)
    variant  = models.ForeignKey(VehicleVariant, on_delete=models.CASCADE)
    category = models.ForeignKey(Category, on_delete=models.CASCADE)   # denorm for facet counts
    brand    = models.ForeignKey(Brand, on_delete=models.CASCADE)      # denorm for facet counts
    position = models.CharField(max_length=24, blank=True)
    class Meta:
        unique_together = [("product", "variant", "position")]
        indexes = [models.Index(fields=["variant", "category"]),
                   models.Index(fields=["variant", "brand"])]
```

**Resolution algorithm** — `apps/fitment/services.py`:

```python
def resolve_variants(product) -> set[int]:
    if product.is_universal:
        return set(VehicleVariant.objects.filter(is_active=True).values_list("id", flat=True))

    def match(f):
        qs = VehicleVariant.objects.filter(
            is_active=True,
            generation_id=f.generation_id,
            year_from__lte=f.year_to,
            year_to__gte=f.year_from,
        )
        if f.trim_id:    qs = qs.filter(trim_id=f.trim_id)
        if f.engine_id:  qs = qs.filter(engine_id=f.engine_id)
        if f.drivetrain: qs = qs.filter(drivetrain=f.drivetrain)
        return set(qs.values_list("id", flat=True))

    fits = list(product.fitments.all())
    included = set().union(*[match(f) for f in fits if not f.is_exclusion] or [set()])
    excluded = set().union(*[match(f) for f in fits if f.is_exclusion] or [set()])
    return included - excluded


def rebuild_product_index(product):
    """Fast (<50ms typical). Runs INLINE on Product/Fitment save — no queue needed."""
    with transaction.atomic():
        FitmentIndex.objects.filter(product=product).delete()
        FitmentIndex.objects.bulk_create([
            FitmentIndex(product=product, variant_id=v, category_id=product.category_id,
                         brand_id=product.brand_id, position=pos)
            for v, pos in variant_position_pairs(product)
        ], batch_size=500, ignore_conflicts=True)
```

**The rule that keeps shared hosting alive:**

| Change | Handling |
|---|---|
| One product / its fitments saved | **inline** in `post_save` — it's milliseconds |
| A `VehicleVariant` added or edited | **queued** — touches every product on that generation |
| Generation year range changed | **queued** |
| Bulk import | **queued**, chunked |

Universal products: don't materialise 50,000 rows per SKU. Flag them and `UNION` them in at query
time — `Q(is_universal=True) | Q(id__in=<index hits>)`.

### 3.5 Cross-references — how mechanics actually search

```python
class PartNumber(models.Model):
    product    = models.ForeignKey(Product, on_delete=models.CASCADE, related_name="part_numbers")
    number     = models.CharField(max_length=64)
    normalized = models.CharField(max_length=64, db_index=True)   # upper, strip -, space, .
    kind       = models.CharField(choices=[("oem","OEM"),("mpn","MPN"),
                                           ("cross","Cross-reference"),("supersede","Supersedes")])
    brand      = models.ForeignKey(Brand, null=True, on_delete=models.SET_NULL)  # OEM no. is Toyota's, not Brembo's
```
A mechanic typing `04465-60280` must land on the right page. `/search?q=` normalizes and hits
`normalized` first — exact match → 302 straight to the product. One query, no full-text.

---

## 4. Background work without Celery (Phase 1)

```python
# apps/jobs/models.py
class Job(models.Model):
    name       = models.CharField(max_length=64)        # "rebuild_generation"
    payload    = models.JSONField(default=dict)
    dedupe_key = models.CharField(max_length=200, blank=True, db_index=True)
    status     = models.CharField(max_length=12, default="queued", db_index=True)  # queued/running/done/failed
    priority   = models.SmallIntegerField(default=5)
    run_after  = models.DateTimeField(default=timezone.now, db_index=True)
    attempts   = models.PositiveSmallIntegerField(default=0)
    cursor     = models.JSONField(default=dict)   # resume point for chunked jobs
    error      = models.TextField(blank=True)
    created_at, finished_at = ...

def enqueue(name, payload=None, dedupe_key="", priority=5, delay=0):
    """dedupe_key stops 500 identical rebuild jobs from one bulk edit."""
    if dedupe_key and Job.objects.filter(dedupe_key=dedupe_key, status="queued").exists():
        return
    return Job.objects.create(name=name, payload=payload or {}, dedupe_key=dedupe_key,
                              priority=priority, run_after=timezone.now() + timedelta(seconds=delay))
```

```python
# apps/jobs/management/commands/run_jobs.py
#   Claims one job at a time. Exits cleanly before the host kills it.
#   MySQL 8 / MariaDB 10.6 support skip_locked — overlapping cron ticks are safe.
def handle(self, *a, **o):
    deadline = time.monotonic() + o["max_seconds"]      # default 240
    while time.monotonic() < deadline:
        with transaction.atomic():
            job = (Job.objects.select_for_update(skip_locked=True)
                   .filter(status="queued", run_after__lte=timezone.now())
                   .order_by("priority", "id").first())
            if not job:
                return
            job.status = "running"; job.attempts += 1; job.save()
        run(job, deadline)     # handler MUST checkpoint into job.cursor and re-queue if it runs long
```

**Chunking is mandatory.** Any handler that could touch >500 rows saves a `cursor`, re-queues
itself, and returns. A job that runs to completion in one tick is a job that gets your process
killed and your account flagged.

**cPanel cron:**
```cron
*/5  *  *  *  *  cd ~/app && ~/venv/bin/python manage.py run_jobs --max-seconds=240 >> ~/logs/jobs.log 2>&1
17   2  *  *  *  cd ~/app && ~/venv/bin/python manage.py rebuild_seo_registry
40   2  *  *  *  cd ~/app && ~/venv/bin/python manage.py build_variant_groups
50   2  *  *  *  cd ~/app && ~/venv/bin/python manage.py build_sitemaps
10   3  *  *  *  cd ~/app && ~/venv/bin/python manage.py fitment_audit --email-report
*/15 *  *  *  *  cd ~/app && ~/venv/bin/python manage.py sync_merchant_feed --delta
30   4  *  *  0  cd ~/app && ~/venv/bin/python manage.py sync_merchant_feed --full
```
Every one of these commands must be **idempotent** and **safe to run twice**. Cron will overlap.

---

## 5. Phases

### Phase 0 — Foundation *(day 1–3)*

**Do this before writing a line of code.** Write the answers into `HOST.md` and commit it:
Python version · Node version offered · MySQL or Postgres · cron minimum interval · **total memory
cap** · `nproc` cap · CPU-second/entry-process limits · **inode limit** · SSH? · can you run two
Passenger apps on one account? If the answer to that last one is no, the whole layout changes —
find out now, not in week 6.

- [ ] Monorepo: `/backend` (Django), `/frontend` (Next.js), `/infra` (cron, deploy scripts)
- [ ] **Backend app:** `api.domain.com` → cPanel "Setup Python App" → `passenger_wsgi.py`,
      settings via `python-decouple` + `.env`
- [ ] `manage.py createcachetable`; `CACHES` → `DatabaseCache`; `SESSION_ENGINE = cached_db`
- [ ] WhiteNoise for Django static (`/admin` assets only — the storefront has its own)
- [ ] **Frontend app:** `domain.com` → cPanel "Setup Node.js App" → startup file `server.js`
      (from `.next/standalone`). `next.config.js`: `output: "standalone"`, `images.remotePatterns`
      → your `/media` host.
- [ ] **Deploy:** build locally in Docker (`node:20-bookworm`) → single tarball → extract to a
      timestamped release dir → symlink swap → `touch tmp/restart.txt`. See §9.
      **The server never builds.**
- [ ] **Cloudflare:** proxy DNS on for both hosts. Cache Rule "Cache Everything" on
      `domain.com/car-parts/*`, `/products/*`, and `api.domain.com/media/*`; **bypass**
      `api.domain.com/*` (except `/media`), `/cart/*`, `/checkout/*`, `/search*`.
      Zone ID + API token into `.env`.
- [ ] `apps/core/cf.py::purge(urls)` — batched (30 URLs/call), fire-and-forget, never blocks a request
- [ ] `REVALIDATE_SECRET` shared between Django and Next (see Phase 4)
- [ ] Smoke test the memory ceiling **now**: run both apps, hit the frontend with
      `ab -n 500 -c 10`, watch cPanel's resource usage graph. If Node OOMs at 10 concurrent, you
      have found your real constraint on day 3 instead of on launch day.

### Phase 1 — Vehicle & fitment core *(week 1–2)*
- [ ] Models §3.1, §3.3, §3.4, §3.5; migrations; admin with `Fitment` inline on `Product`
- [ ] `Job` model + `run_jobs` + `enqueue()`
- [ ] `resolve_variants()`, `rebuild_product_index()` inline; `rebuild_generation` queued
- [ ] **Tests first-class:** overlap, `OPEN_YEAR`, exclusions, universal, null-trim wildcard
- [ ] Seed fixture, real Kenya vehicles: Prado J120/J150, Harrier XU60/XU80, CX-5 KF, Vitz,
      Fielder, Hilux GUN125, Demio, Note, Axio, Premio, Probox
- **Exit gate:** `FitmentIndex` matches a brute-force recomputation in a property test, and a
  generation rebuild of 2,000 products completes across cron ticks without a single timeout.

### Phase 2 — Catalog *(week 2–3)*
- [ ] Brand, Category, Product, ProductImage, Offer, StockMovement
- [ ] Pillow derivative pipeline on upload (1200/600/300 WebP) — never at request time
- [ ] Bulk import: upload XLSX → `ImportBatch` staging rows → validate → report → commit as a
      chunked Job. **Dry-run is the default; `--live` required to write.**
- [ ] Import keyed on `sku`, fully idempotent, re-runnable
- [ ] Admin actions: "Copy fitment from product X", "Bulk add fitment to selection"

### Phase 3 — SEO Page Registry *(week 3–4)* ← the strategic core

```python
class SeoPage(models.Model):
    KIND = [("vehicle","Vehicle storefront"),("vehicle_category","Vehicle + category"),
            ("category","Category"),("brand","Brand"),("product","Product")]
    kind          = models.CharField(max_length=24, choices=KIND, db_index=True)
    path          = models.CharField(max_length=400, unique=True)
    variant_group = models.ForeignKey("vehicles.VariantGroup", null=True, on_delete=models.CASCADE)
    category      = models.ForeignKey(Category, null=True, on_delete=models.CASCADE)
    product       = models.ForeignKey(Product, null=True, on_delete=models.CASCADE)

    product_count = models.PositiveIntegerField(default=0, db_index=True)
    directive     = models.CharField(default="noindex", db_index=True,
                        choices=[("index","index"),("noindex","noindex"),("canonical","canonical")])
    canonical_to  = models.CharField(max_length=400, blank=True)
    priority      = models.FloatField(default=0.5)

    title            = models.CharField(max_length=200, blank=True)
    meta_description = models.CharField(max_length=320, blank=True)
    h1               = models.CharField(max_length=200, blank=True)
    intro_html       = models.TextField(blank=True)

    manual_override  = models.BooleanField(default=False)   # admin wins over the rule engine
    impressions_30d  = models.PositiveIntegerField(default=0)   # from GSC, Phase 8
    clicks_30d       = models.PositiveIntegerField(default=0)
    last_computed    = models.DateTimeField(auto_now=True)
```

**Rule engine** — `apps/seo/rules.py`, run nightly by `rebuild_seo_registry`:

| Condition | Directive |
|---|---|
| product active, has price, ≥1 image | `index` |
| product inactive / OOS >60 days | `noindex`, still 200 |
| vehicle storefront, `count >= 10` | `index` |
| vehicle storefront, `1 <= count < 10` | `noindex, follow` |
| vehicle storefront, `count == 0` | `410 Gone`, absent from sitemap |
| vehicle+category, `count >= 5` | `index` |
| vehicle+category, `count < 5` | `noindex`, canonical → parent storefront |
| trim page whose product set == parent generation's | `canonical` → generation page |
| any `?brand=` / `?sort=` / `?page=` URL | `noindex, follow` + canonical → clean path |
| `manual_override = True` | admin value wins, engine skips the row |

**`VariantGroup` — the anti-duplicate weapon:**

```python
class VariantGroup(models.Model):
    """
    A set of VehicleVariants sharing an IDENTICAL resolved product set.
    ONE SEO page per group. Prado TX 2018 and Prado TX 2019 → same group → one URL.
    """
    generation     = models.ForeignKey(VehicleGeneration, on_delete=models.CASCADE)
    trim           = models.ForeignKey(VehicleTrim, null=True, on_delete=models.CASCADE)
    engine         = models.ForeignKey(VehicleEngine, null=True, on_delete=models.CASCADE)
    year_from, year_to = ...
    slug_years     = models.CharField(max_length=16)                 # "2018-2023"
    fingerprint    = models.CharField(max_length=64, db_index=True)  # sha256 of sorted product ids
    canonical_path = models.CharField(max_length=400, unique=True)
    product_count  = models.PositiveIntegerField(default=0)
    variants       = models.ManyToManyField(VehicleVariant, related_name="groups")
```

`build_variant_groups` (nightly, chunked): for each variant compute the sha256 of its sorted
product-id list → variants sharing a fingerprint within a generation collapse into one group →
one indexed URL, year span derived from the group's min/max.

This is how you publish **~8,000 strong pages instead of 750,000 thin ones**, automatically,
forever, with no editorial team.

- [ ] `build_sitemaps` writes **static XML files** to `/static/sitemaps/` — shards ≤ 45,000 URLs,
      real `lastmod`, only `directive=index`. Never generate sitemaps on request; Google will hit
      them hard enough to trip your CPU limit.
- [ ] `robots.txt`: disallow `/search`, `/cart`, `/checkout`, `*?sort=`, `*?page=`
- [ ] IndexNow ping on registry change (one cheap POST, no API key ceremony)

### Phase 4 — The API *(week 4)*

DRF, read-only, aggressively shaped for the frontend. **One page = one API call.** Do not make
Next.js stitch four endpoints together to render a storefront — every extra round trip is a
Passenger process held open on a host that counts them.

```
GET /api/v1/vehicles/makes/
GET /api/v1/vehicles/makes/{make}/models/
GET /api/v1/vehicles/models/{model}/generations/
GET /api/v1/vehicles/generations/{gen}/trims/
GET /api/v1/vehicles/generations/{gen}/engines/
GET /api/v1/vehicles/resolve/?make=&model=&generation=&trim=&engine=&year=
      → { variant_id, group_id, canonical_url, display_name, product_count }
GET /api/v1/vehicles/resolve-plate/?plate=KDA123A            (Phase 9)

GET /api/v1/page/?path=/car-parts/toyota/.../2018-2023/      ← THE endpoint
      → { seo: {title, meta_description, h1, canonical, directive, intro_html},
          hero, breadcrumbs, category_tiles, products[], facets{}, pagination,
          related_links{other_trims, other_generations, popular_categories},
          structured_data[] }
      → 404 when no SeoPage; 410 when directive == "410"

GET /api/v1/products/{slug}/     → product, offer, images, fits_summary, also_fits[], structured_data
GET /api/v1/products/{slug}/fits/?page=   → paginated "Fits these vehicles" table
GET /api/v1/search/?q=           → { redirect_to } for part-number/vehicle-intent hits, else results
GET /api/v1/seo/changed/?since=  → paths to revalidate (frontend cron pulls this)
```

- [ ] `path=` lookup resolves `SeoPage` in **one indexed query**. The API returns
      `directive` and `canonical`. **Next.js never decides indexability.**
- [ ] Every read endpoint: `Cache-Control: public, s-maxage=3600` + `ETag`, and a
      `DatabaseCache` layer keyed on `(path, page, sort, filters)`
- [ ] `assertNumQueries` on every endpoint. ≤ 12. N+1 is survivable on a VPS; here it's an outage.
- [ ] Facets from `FitmentIndex` `.values("brand").annotate(Count)` — one query, denorm columns earn it
- [ ] `X-Robots-Tag` never set by the API — the frontend owns response headers

### Phase 5 — Next.js storefront *(week 5–7)*

```
frontend/app/
  car-parts/[make]/page.tsx
  car-parts/[make]/[model]/page.tsx
  car-parts/[make]/[model]/[generation]/page.tsx
  car-parts/[make]/[model]/[generation]/[trim]/[years]/page.tsx            ← storefront template
  car-parts/[make]/[model]/[generation]/[trim]/[years]/[category]/page.tsx ← category template
  products/[slug]/page.tsx
  [...category]/page.tsx
  search/page.tsx
  api/revalidate/route.ts                                                  ← Django calls this
components/ VehicleSelector · GarageBanner · FitmentTable · FacetSidebar · ProductCard
```

- [ ] **Server components only** for anything above the fold. The only `"use client"` components in
      this build are `VehicleSelector`, `FacetSidebar`, and `AddToCart`. Nothing else. A parts
      storefront is a document, not an app.
- [ ] `generateMetadata` reads `seo.title / meta_description / canonical / directive` from
      `/api/v1/page/`. `directive: noindex` → `robots: { index: false, follow: true }`.
      `410` → `notFound()` after setting the status via a route handler.
- [ ] **`generateStaticParams` capped at the top ~1,500 groups** by popularity. Everything else is
      on-demand ISR. This is an inode decision, not a performance one — pre-rendering 8,000 pages
      writes tens of thousands of files into `.next` and will trip cPanel's file limit.
- [ ] `export const revalidate = 3600` on SEO pages; `fetch(..., { next: { tags: ['product:123'] }})`
- [ ] **On-demand revalidation:** `Offer.save()` → Django POSTs `{paths, tags, secret}` to
      `https://domain.com/api/revalidate` → `revalidatePath()` / `revalidateTag()` → **then**
      `cf.purge(paths)`. Order matters: purge Cloudflare *after* Next has dropped its own cache, or
      the edge just re-caches the stale page.
- [ ] Cloudflare `Cache-Control: public, s-maxage=86400, stale-while-revalidate=604800` on SEO pages.
      Origin gets hit roughly once per page per day. **This is what makes shared hosting viable** —
      ISR is your second line, Cloudflare is your first.
- [ ] Breadcrumbs: Home › Toyota › Prado › J150 › TX › 2018–2023 › Brake Pads
- [ ] Internal linking blocks (SEO gold, ~free, all from `related_links`):
      "Other trims of this generation" · "Other generations" · "Popular categories for this
      vehicle" · **"Also fits"** on product pages, linking out to other vehicle storefronts
- [ ] Pagination hard cap at page 5 for crawlers; deeper pages `noindex`
- [ ] `next/image` with `remotePatterns` → `/media`, but the derivatives are **already generated by
      Pillow** (Phase 2). Do not let the Node process do image optimisation — that's the fastest
      way to get OOM-killed. Set `images: { unoptimized: true }` and serve pre-sized WebP.
- [ ] Perf budget: LCP < 2.5s on Safaricom 4G, CLS < 0.05, JS bundle < 90KB gzipped on a
      storefront page. Test on a real mid-range Android, not a MacBook.

### Phase 6 — Search & the garage *(week 7)*
- [ ] **Part-number fast path:** normalize → `PartNumber.normalized` exact → API returns
      `{redirect_to}` → frontend `redirect()`. One query, no full-text.
- [ ] **Vehicle intent parser:** `"prado 2018 brake pads"` → `{make: toyota, model: prado (alias),
      year: 2018, category: brake-pads}` → **redirect to the SEO storefront URL.**
      Your search box becomes a router into your SEO pages. Nothing else you build converts better.
- [ ] `ProductSearchDoc` table: `product_id` + one `text` column, rebuilt on product save, with a
      raw-SQL migration adding `ALTER TABLE ... ADD FULLTEXT(text)` (use the `ngram` parser on
      MySQL). Query with `MATCH() AGAINST(... IN BOOLEAN MODE)`. Postgres path: `SearchVector` + GIN.
- [ ] Fallback: `icontains` on name/mpn, capped at 50 rows. Ugly, works, costs nothing.
- [ ] `VehicleSelector` client component: Make → Model → Generation → Trim → Engine → Year, each
      step a `fetch` to the vehicles API, then `router.push(canonical_url)`. Renders as plain
      `<select>`s server-side first so it works before hydration — and so Googlebot sees the links.
- [ ] **My Garage:** the chosen variant in an httpOnly cookie + on the user account. Read it in a
      server component; every category page auto-filters to that car. Biggest conversion lever in
      the whole build, ~40 lines.
      ⚠️ **The cookie must not vary a cached page.** Render the garage banner in a
      `<Suspense>`-wrapped dynamic segment, or Cloudflare will serve one person's Prado to
      everyone. This is the single most likely bug in this build.
- [ ] Sticky banner: `✓ Showing parts for your Toyota Prado TX 2018 — Change`

### Phase 7 — Structured data *(week 7–8)*
**Generated in Django** (`product.structured_data`, a cached property), returned by the API, and
injected by Next.js as a `<script type="application/ld+json">` in a **server component**. Never
build JSON-LD in the frontend — the moment schema lives in two places it drifts, and Google reads
the drift, not your intent.

```jsonc
{
  "@context": "https://schema.org",
  "@type": "Product",
  "name": "Brembo Front Brake Pads P83-145",
  "sku": "BRM-P83145", "mpn": "P83-145",
  "brand": {"@type": "Brand", "name": "Brembo"},
  "image": ["https://.../1200.webp"],
  "isAccessoryOrSparePartFor": [                     // ← the fitment signal Google reads
    {"@type": "Product", "name": "Toyota Land Cruiser Prado J150 TX 2.8L Diesel 2018-2023"}
  ],
  "offers": {
    "@type": "Offer",
    "priceCurrency": "KES", "price": "14500.00",
    "availability": "https://schema.org/InStock",
    "itemCondition": "https://schema.org/NewCondition",
    "url": "https://.../products/brembo-p83-145-front-brake-pads/",
    "priceValidUntil": "2026-12-31",
    "shippingDetails": {...}, "hasMerchantReturnPolicy": {...}
  }
  // "aggregateRating" ONLY when real reviews exist. Faking it = Merchant suspension.
}
```
- [ ] `BreadcrumbList` everywhere · `ItemList` on storefront/category · `Organization` + `WebSite`
      + `SearchAction` on home
- [ ] `FAQPage` on storefronts, auto-generated: *"What brake pads fit a Toyota Prado TX 2018?"*
- [ ] Validate 20 sample URLs against the Rich Results Test each release (manual checklist is fine)

### Phase 8 — Google Merchant Center *(week 8)*
No Merchant API SDK on shared hosting to start — **XML feed on disk is the pragmatic path**.

- [ ] Verify + claim domain in GMC. Target: Kenya, KES, English + Swahili.
- [ ] `sync_merchant_feed` (cron) writes `/static/feeds/google-shopping.xml`. GMC fetches it on a
      schedule. Zero origin CPU at fetch time, served by Cloudflare.
- [ ] `--delta` every 15 min writes a small supplemental feed for price/stock changes only.

| GMC attribute | Source |
|---|---|
| `id` | `product.sku` |
| `title` | `"{brand} {name} — Fits {top_vehicle}"` (≤150 chars, brand+part front-loaded) |
| `description` | generated, includes a fitment sentence |
| `link` | canonical product URL |
| `image_link` / `additional_image_link` | primary + up to 10 |
| `availability`, `price`, `sale_price` | live from `Offer` |
| `brand`, `gtin`, `mpn`, `identifier_exists` | `false` only when genuinely neither exists |
| `condition` | new / refurbished / used |
| `google_product_category` | `category.google_category` |
| `product_type` | your own breadcrumb path |
| `shipping`, `shipping_weight` | delivery zone + `product.weight_kg` |
| `custom_label_0..4` | **make** / model / margin band / velocity / stock age |

> `custom_label_0 = make` is what lets you bid separately on Toyota vs Mercedes parts later.
> Set it now — you cannot backfill campaign history.

- [ ] Same generator emits Facebook Catalog + Jiji feeds. One mapping layer, three channels.
- [ ] Enable GMC's automatic product source as a **safety net**, not the primary pipeline.
- [ ] Weekly cron pulls GMC disapproval issues → Django admin dashboard → email alert.
- [ ] Migrate to Merchant API push only if/when you move to a VPS.

### Phase 9 — Commerce *(week 8–10)*
- [ ] Cart (signed cookie for guests, DB for users), guest checkout, county/town delivery zones
- [ ] **Fitment guard at add-to-cart:** if a garage vehicle is set and the product is not in that
      variant's `FitmentIndex` → interstitial: *"This may not fit your Prado TX 2018. Continue?"*
      One screen. It is the difference between a parts store and a returns department.
- [ ] M-Pesa Daraja STK Push + callback endpoint (**CSRF-exempt, IP-allowlisted, idempotent by
      `CheckoutRequestID`**) + an order state machine that never double-credits
- [ ] Callbacks are unreliable on shared hosting — add a `reconcile_mpesa` cron that queries
      transaction status for any order stuck in `pending` >5 min
- [ ] Order → Fulfilment → Shipment; email + SMS (Africa's Talking), sent via the Job queue
- [ ] Reviews with a verified-purchase flag → feeds `aggregateRating` honestly
- [ ] GA4 (client-side, free) + weekly Search Console API pull writing `impressions_30d` /
      `clicks_30d` back onto `SeoPage`
- [ ] **The feedback loop:** impressions but no clicks → flag for title/meta rewrite.
      Clicks but no products → **sourcing signal for the buying team.**

### Phase 10 — Kenya hardening *(week 10+)*
- [ ] Plate/VIN → variant resolver, cached forever in `VehicleRegistrationLookup`
- [ ] KRA eTIMS invoice submission on order paid (queued Job, retried)
- [ ] Swahili locale + `hreflang` (`en-KE`, `sw-KE`)
- [ ] WhatsApp deep-link on every product: "Ask about fitment"
- [ ] Garage/mechanic B2B tier: price lists, credit terms, bulk quote → order
- [ ] JDM nuance: `market` on variant matters — a JP-import Harrier ≠ a KE-spec Harrier

---

## 6. Shared-hosting survival rules

1. **No query at request time that isn't an index seek.** If you need a `GROUP BY` over 10k rows to
   render a page, pre-compute it into a column.
2. **Nothing runs longer than ~4 minutes.** Chunk it, cursor it, re-queue it.
3. **Every cron command is idempotent.** They will overlap. Assume it.
4. **Cloudflare absorbs the crawl.** If Googlebot is hitting your origin for `/car-parts/*`, your
   cache rules are wrong — fix that before optimising a single query.
5. **Never resize an image in a request.**
6. **Never generate a sitemap in a request.**
7. **`assertNumQueries` on every API endpoint.** N+1 is survivable on a VPS. Here it's an outage.
8. **Watch the inode count, not the disk quota.** Image derivatives + `.next/cache` will hit
   cPanel's file limit long before you fill the disk. Move `/media` to Cloudflare R2 the moment you
   cross ~5k products.
9. **Never build on the server.** `next build`, `npm ci`, Tailwind compilation — all on your machine, in Docker. The
   server runs `node server.js` and nothing else. And never touch cPanel's "Run NPM Install".
10. **Node is not allowed to optimise images.** `images.unoptimized: true`, pre-sized WebP from
    Pillow. Sharp on a shared host is an OOM waiting for a busy Tuesday.
11. **One page = one API call.** Every extra round trip holds a Python *and* a Node process open
    simultaneously. You are counting processes now, not milliseconds.
12. **Back up nightly to off-host storage.** Shared hosting backups are a courtesy, not a contract.

---

## 7. Anti-patterns — reject on sight

| ✗ Don't | ✓ Do |
|---|---|
| One product row per car it fits | One product + `Fitment` rows |
| A row per year | `year_from` / `year_to` + `OPEN_YEAR` |
| `year_to = NULL` | `year_to = 9999` (indexable) |
| Range math at request time | `FitmentIndex`, pre-computed |
| Materialise universal parts into 50k rows | Flag + `UNION` at query time |
| Google indexes every URL | `SeoPage.directive` decides |
| Next.js computing fitment or SEO directives | Django owns truth; Next renders it |
| JSON-LD built in the frontend | Generated in Django, injected as-is |
| `next build` on the server | Build locally in Docker, ship a tarball |
| Uploading `.next` and calling it done | `standalone` + `.next/static` + `public` |
| Clicking cPanel's "Run NPM Install" | The server installs nothing, ever |
| `sharp` / `next/image` optimisation on the host | Pillow derivatives + `unoptimized: true` |
| Garage cookie read on a cached page | `<Suspense>` boundary, or you leak one user's car to all |
| `generateStaticParams` over every group | Cap at ~1,500 — inodes, not speed |
| Sitemaps generated per request | Static XML written by cron |
| Merchant feed "added later" | Feed mapping from Phase 2 |
| Trust supplier CSV fitment | `source` + `confidence` + `verified_by` |
| `aggregateRating` with no reviews | Suspension. Never. |
| Thin trim pages for volume | Fewer, denser, canonicalised pages |

---

## 8. Definition of done

1. Add a product with **one** fitment rule → it appears on every correct storefront, in the
   sitemap (if it clears threshold), in the GMC feed, and in JSON-LD — **no manual page work.**
2. Change a price in admin → `revalidatePath` + Cloudflare purge → live < 60s; in GMC < 15 min.
3. `fitment_audit` returns zero criticals.
4. A storefront with 0 products returns 410 from both API and frontend, and is in no sitemap.
5. Every API endpoint: ≤ 12 queries, asserted in tests.
6. Cloudflare cache hit ratio on `/car-parts/*` > 90%.
7. Lighthouse mobile ≥ 90 and JS < 90KB gzipped on storefront, category, and product templates.
8. A deploy is: one tarball up, extract, symlink swap, restart, purge — and never a build step.
9. Both Passenger apps stay inside the memory cap under `ab -n 2000 -c 20`.

---

## 9. Deploy — build locally, upload the artifact

The plan is: build on your machine, upload the result. Correct instinct. But **`.next` alone is
not the artifact** — that is the mistake that costs everyone their first evening.

### 9.1 What `output: "standalone"` actually produces

```
.next/standalone/     ← server.js + a PRUNED node_modules + package.json
.next/static/         ← NOT copied in. You must copy it.
public/               ← NOT copied in. You must copy it.
```

Next does not assemble these for you. The deployable tree you upload is:

```
standalone/
├── server.js              ← Passenger startup file
├── package.json
├── node_modules/          ← pruned by build-time tracing
├── .next/
│   ├── BUILD_ID
│   ├── server/
│   └── static/            ← you copied this in
└── public/                ← you copied this in
```

Upload `.next/standalone` **without** `.next/static` and the site loads with zero CSS and every JS
chunk 404ing. It looks like a broken deploy; it's actually a missing copy step.

### 9.2 The build script (`infra/build.sh`)

```bash
#!/usr/bin/env bash
set -euo pipefail
cd frontend

rm -rf .next dist
npm ci                       # ci, not install — respect the lockfile
npm run build                # next build, with output: "standalone"

rm -rf ../dist && mkdir -p ../dist
cp -r .next/standalone/.     ../dist/
mkdir -p ../dist/.next
cp -r .next/static           ../dist/.next/static     # ← the step everyone forgets
cp -r public                 ../dist/public           # ← and this one

cd .. && tar -czf dist.tgz -C dist .
echo "artifact: $(du -sh dist.tgz | cut -f1)"
```

**Upload `dist.tgz`, not the directory.** `node_modules` is 15,000+ tiny files; FTPing it takes
hours and hammers your inode count twice (once uploading, once existing). One tarball, extract over
SSH or via cPanel File Manager. If your plan has no SSH, File Manager's extract works fine.

### 9.3 The five things that will break a local build on the host

1. **Platform mismatch — the big one.** `node_modules` in standalone contains platform-specific
   binaries (`@next/swc-*`). Build on macOS ARM or Windows, deploy to Linux x64, and you get a
   runtime crash that reads like nonsense. Fixes, in order of preference:
   - Build inside Docker: `node:20-bookworm`, mount `frontend`, run `build.sh`. Deterministic, and
     it matches the host. **Do this.**
   - Or build in WSL2 (if you're on Windows).
   - Or `npm ci --os=linux --cpu=x64` and pray.
   Since we set `images.unoptimized: true`, `sharp` is out of the picture, which removes the worst
   offender — but SWC alone is enough to ruin an evening.

2. **Node major version mismatch.** Build on 22, host runs 18 → cryptic failures. Pin it:
   `"engines": { "node": "20.x" }`, and put the host's actual version in `HOST.md` on day 1.

3. **`NEXT_PUBLIC_*` is baked at build time.** Building locally means your local `.env` values get
   compiled into the client bundle. If `NEXT_PUBLIC_API_URL=http://localhost:8000` ships to
   production, every page fetches localhost from the customer's phone. Use `.env.production` and
   have `build.sh` assert on it:
   ```bash
   grep -q "api.domain.com" .env.production || { echo "WRONG API URL"; exit 1; }
   ```
   Server-only vars (`REVALIDATE_SECRET`) are read at runtime — set those in the cPanel Node app's
   environment panel, not in the build.

4. **Deploying is not atomic.** Uploading over a live app mid-extract means a window where
   `.next/static` holds new chunks and `.next/server` holds old ones — clients get a `BUILD_ID`
   mismatch and hard 404s. Extract to a new directory, then swap:
   ```bash
   tar -xzf dist.tgz -C ~/releases/$(date +%s)
   ln -sfn ~/releases/<new> ~/app_current      # cPanel Node app points at app_current
   touch ~/app_current/tmp/restart.txt
   ```
   Keep the last 3 releases. Rollback becomes one `ln -sfn`.

5. **Do NOT click "Run NPM Install" in cPanel.** Ever. The standalone `node_modules` is already
   pruned and traced; cPanel's install will pull dev dependencies, blow past your inode limit, and
   possibly get the build killed mid-flight. The server installs nothing. It runs `server.js`.

### 9.4 Passenger wiring

- cPanel → Setup Node.js App → **Application startup file:** `server.js`
- Passenger sets `PORT`; standalone's `server.js` reads `process.env.PORT`. It just works.
- Set `HOSTNAME=0.0.0.0` in the app's env vars if it binds wrong.
- Restart = `touch tmp/restart.txt`. Never kill the process by hand.

### 9.5 Django deploys separately (and usually doesn't)

```bash
cd ~/backend && git pull
~/venv/bin/pip install -r requirements.txt      # only when it changed
~/venv/bin/python manage.py migrate
~/venv/bin/python manage.py collectstatic --noinput
touch ~/backend/tmp/restart.txt
```
Backend and frontend version independently. That's a feature: 90% of your changes are catalog data
and never touch either codebase.

### 9.6 ISR cache and uploads

A fresh upload wipes the ISR cache — pages regenerate on first hit. That's fine and expected. Two
consequences:

- **Deploy at 2am Nairobi time.** Right after a deploy, every page is a cache miss until Cloudflare
  refills. Deploying at noon means Node cold-rendering under live traffic on a shared host.
- **Purge Cloudflare after a deploy**, or the edge serves the old build's HTML pointing at chunk
  filenames that no longer exist. `cf.purge_everything()` on deploy — the one time it's justified.

### 9.7 Deploy checklist

- [ ] `build.sh` runs in Docker `node:20-bookworm`, not on your host OS
- [ ] `.env.production` asserted before build
- [ ] `.next/static` and `public` copied into the artifact
- [ ] Artifact is a single tarball
- [ ] Extract to a timestamped release dir, symlink swap, `touch tmp/restart.txt`
- [ ] Cloudflare purge after restart
- [ ] Smoke test: `curl -sI https://domain.com/car-parts/toyota/... | grep -E "200|x-nextjs-cache"`
- [ ] Last 3 releases retained for rollback

---

# Why this makes the site great

**1. It wins searches your competitors can't reach.**
Nobody in Kenya searches "brake pads". They search *"brake pads for prado tx 2018"*. Generic
catalogs can't answer that — they have a category page and a search box. You will have a real,
crawlable, dense page for that exact question, times several thousand, generated from data you
were going to enter anyway.

**2. The `VariantGroup` fingerprint is the whole SEO game.**
The failure mode of every fitment site is thin-content bloat: 750,000 near-identical pages, Google
crawls 4% of them, ranks none. Collapsing variants by product-set fingerprint publishes the
*smallest set of maximally distinct pages*. Crawl budget lands on pages that are actually
different from each other. Fewer pages, more traffic. On shared hosting this stops being merely
smart and becomes survival: you cannot serve 750,000 URLs to Googlebot, and now you never have to.

**3. One product, many cars — the catalog compounds.**
The 5,000th product doesn't take longer to add than the 5th. Each new fitment rule instantly
enriches every storefront it touches; each new generation instantly inherits every compatible part
already in the system. Duplicated-SKU catalogs get exponentially more expensive and eventually
collapse under their own inconsistency. Yours gets denser and cheaper per page.

**4. Two Google pipelines instead of one.**
Organic SEO brings the researcher ("what fits my car?"). Merchant/Shopping brings the buyer
("who has it, how much, in stock?"). Most Kenyan parts sites have neither properly. Having both,
fed by the same Django tables with zero drift between them, is a structural moat — not a campaign
you have to keep paying for.

**5. Fitment confidence is the actual product.**
Buying parts online in Kenya fails on one fear: *will it actually fit?* The garage, the plate
lookup, the sticky "showing parts for your Prado", the add-to-cart guard, the "also fits" table —
together these are the reason someone buys from you instead of driving to Kirinyaga Road. That's
not a feature list. It's the value proposition, and it falls straight out of the data model. You
cannot retrofit it onto a duplicated-SKU catalog.

**6. The SEO registry quietly becomes business intelligence.**
Once `impressions_30d` lands on `SeoPage`, you know which vehicles Kenya is searching for that you
*don't stock* — a sourcing roadmap generated by your own website, monthly, for free. Nobody else
in the market has that. SEO infrastructure turns into a purchasing advantage.

**7. The split is clean because Django keeps the truth.**
The usual failure of a headless build is two codebases slowly disagreeing — the frontend computing
its own canonical, its own schema, its own "is this in stock". Here Next.js computes nothing. It
asks `/api/v1/page/?path=...` and renders what comes back, including the SEO directive and the
JSON-LD. That's why the second codebase costs you almost nothing: it has no opinions. And it buys
you a fast, modern storefront — real interactivity in the vehicle selector and facets, instant
client-side navigation between categories — on a host that costs less than lunch.

**8. It's boringly extensible, and portable.**
Laptops and phones drop in as `Category.kind = "general"` and skip fitment entirely — same models,
same offers, same feed, same templates. Multi-seller is one `OneToOne` → `ForeignKey` migration.
Uganda/Tanzania is a `market` field and a currency. And nothing here is host-specific: the day the
catalog outgrows shared hosting, you move Django to a VPS and the frontend to Vercel/a Node box,
swap `DatabaseCache` for Redis and `Job` for Celery in two settings changes, and delete nothing.
The `.next/standalone` bundle you're already shipping is the same artifact any host wants.

**The two risks, ranked:**

1. **Phase 1–2 being wrong.** Get the taxonomy or the fitment resolver wrong and every later phase
   inherits the error and gets more expensive to fix. Build the resolver, write the property tests,
   run `fitment_audit` clean — and only then write a component.
2. **The host, not the code.** Two Passenger apps on a shared account is a real constraint and the
   plan respects it, but it is the thing most likely to bite you: an OOM-killed Node process at 3am
   during a crawl, or an inode ceiling you hit at 6,000 products. Phase 0's memory smoke test and
   the inode discipline in §6 exist for exactly this. Do them on day 3. When the numbers finally
   say move, moving is a deploy — not a rewrite.
