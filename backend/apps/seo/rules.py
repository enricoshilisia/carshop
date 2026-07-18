"""The SEO rule engine. Run nightly by `rebuild_seo_registry`.

| Condition                                      | Directive                          |
|------------------------------------------------|------------------------------------|
| product active, has price, ≥1 image            | index                              |
| product inactive                               | noindex (still 200)                |
| vehicle storefront, count >= 10                | index                              |
| vehicle storefront, 1 <= count < 10            | noindex, follow                    |
| vehicle storefront, count == 0                 | 410 Gone, absent from sitemap      |
| vehicle+category, count >= 5                   | index                              |
| vehicle+category, count < 5                    | noindex, canonical → parent        |
| manual_override = True                         | admin value wins, engine skips row |
"""
from django.conf import settings
from django.db.models import Count, Q

from apps.catalog.models import Category, Product
from apps.fitment.models import FitmentIndex
from apps.seo.models import SeoPage
from apps.seo.paths import group_category_path, group_path, product_path
from apps.vehicles.models import VariantGroup


def _upsert(path, defaults):
    page = SeoPage.objects.filter(path=path).first()
    if page and page.manual_override:
        return page
    if page:
        for k, v in defaults.items():
            setattr(page, k, v)
        page.save()
        return page
    return SeoPage.objects.create(path=path, **defaults)


def _vehicle_texts(group: VariantGroup) -> dict:
    gen = group.generation
    name_bits = [gen.model.make.name, gen.model.name, gen.code]
    if group.trim_id:
        name_bits.append(group.trim.name)
    vehicle = " ".join(name_bits)
    years = group.slug_years.replace("-", "–")
    return {
        "title": f"{vehicle} {years} Parts & Spares in Kenya | Corporation Premium",
        "h1": f"{vehicle} ({years}) Parts",
        "meta_description": (
            f"Genuine and aftermarket parts for the {vehicle} {years}. "
            f"{group.product_count} parts in stock with verified fitment, "
            "delivered across Kenya. Pay via M-Pesa."
        )[:320],
    }


def rebuild_registry() -> dict:
    """Idempotent full rebuild. Returns counters for the log."""
    stats = {"vehicle": 0, "vehicle_category": 0, "product": 0}

    # --- vehicle storefront pages, one per VariantGroup -------------------
    for group in VariantGroup.objects.select_related(
        "generation__model__make", "trim"
    ).all():
        count = group.product_count
        if count >= settings.SEO_MIN_PRODUCTS_STOREFRONT:
            directive, canonical = "index", ""
        elif count >= 1:
            directive, canonical = "noindex", ""
        else:
            directive, canonical = "410", ""
        _upsert(
            group.canonical_path,
            {
                "kind": "vehicle",
                "variant_group": group,
                "product_count": count,
                "directive": directive,
                "canonical_to": canonical,
                "priority": 0.8 if directive == "index" else 0.3,
                **_vehicle_texts(group),
            },
        )
        stats["vehicle"] += 1

        # --- vehicle + category pages under this group --------------------
        variant_ids = list(group.variants.values_list("id", flat=True))
        cat_counts = (
            FitmentIndex.objects.filter(variant_id__in=variant_ids, product__is_active=True)
            .values("category")
            .annotate(n=Count("product", distinct=True))
        )
        universal = Product.objects.filter(is_universal=True, is_active=True).values(
            "category"
        ).annotate(n=Count("id"))
        merged: dict[int, int] = {}
        for row in list(cat_counts) + list(universal):
            merged[row["category"]] = merged.get(row["category"], 0) + row["n"]
        categories = {c.id: c for c in Category.objects.filter(id__in=merged)}
        for cat_id, n in merged.items():
            cat = categories.get(cat_id)
            if not cat:
                continue
            path = group_category_path(group, cat.slug)
            if n >= settings.SEO_MIN_PRODUCTS_VEHICLE_CATEGORY:
                directive, canonical = "index", ""
            else:
                directive, canonical = "canonical", group.canonical_path
            texts = _vehicle_texts(group)
            gen = group.generation
            vehicle = f"{gen.model.make.name} {gen.model.name} {gen.code}"
            _upsert(
                path,
                {
                    "kind": "vehicle_category",
                    "variant_group": group,
                    "category": cat,
                    "product_count": n,
                    "directive": directive,
                    "canonical_to": canonical,
                    "priority": 0.7 if directive == "index" else 0.2,
                    "title": f"{cat.name} for {vehicle} {group.slug_years} | Corporation Premium",
                    "h1": f"{cat.name} — {vehicle} ({group.slug_years.replace('-', '–')})",
                    "meta_description": texts["meta_description"],
                },
            )
            stats["vehicle_category"] += 1

    # --- product pages -----------------------------------------------------
    products = Product.objects.select_related("brand", "offer").annotate(
        image_count=Count("images", distinct=True)
    )
    for p in products:
        has_offer = getattr(p, "offer", None) is not None
        indexable = p.is_active and has_offer and p.image_count >= 1
        _upsert(
            product_path(p),
            {
                "kind": "product",
                "product": p,
                "product_count": 1,
                "directive": "index" if indexable else "noindex",
                "priority": 0.6,
                "title": f"{p.brand.name} {p.name} | Corporation Premium Kenya",
                "h1": p.name,
                "meta_description": (p.description or p.name)[:320],
            },
        )
        stats["product"] += 1

    # Trim page whose product set == parent generation's → canonical to parent.
    _canonicalise_duplicate_trims()
    return stats


def _canonicalise_duplicate_trims():
    groups = list(
        VariantGroup.objects.select_related("generation").order_by("generation_id", "trim_id")
    )
    by_gen: dict[int, list[VariantGroup]] = {}
    for g in groups:
        by_gen.setdefault(g.generation_id, []).append(g)
    for gen_groups in by_gen.values():
        parents = [g for g in gen_groups if g.trim_id is None]
        if not parents:
            continue
        parent = parents[0]
        for g in gen_groups:
            if g.trim_id and g.fingerprint == parent.fingerprint:
                SeoPage.objects.filter(path=g.canonical_path, manual_override=False).update(
                    directive="canonical", canonical_to=parent.canonical_path
                )
