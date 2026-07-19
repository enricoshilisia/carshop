"""Read-only DRF API. One page = one API call — Next.js never stitches
endpoints together, and never computes fitment or SEO directives itself.
"""
from django.core.cache import cache
from django.db.models import Count, Q
from django.utils import timezone
from rest_framework.decorators import api_view
from rest_framework.response import Response

from apps.api import serializers as s
from apps.catalog.models import Category, Product
from apps.catalog.search import parse_vehicle_intent, part_number_lookup, text_search
from apps.fitment.models import FitmentIndex
from apps.seo import structured_data as sd
from apps.seo.models import SeoPage
from apps.vehicles.models import (
    VehicleEngine,
    VehicleGeneration,
    VehicleMake,
    VehicleModel,
    VehicleTrim,
    VehicleVariant,
    VariantGroup,
)

PAGE_SIZE = 24
CACHE_TTL = 3600


def _cached(request, response_data, status=200):
    resp = Response(response_data, status=status)
    resp["Cache-Control"] = "public, s-maxage=3600"
    return resp


# --------------------------------------------------------------------------
# Vehicle taxonomy — powers the VehicleSelector
# --------------------------------------------------------------------------

@api_view(["GET"])
def makes(request):
    data = [s.make_dict(m) for m in VehicleMake.objects.filter(is_active=True)]
    return _cached(request, data)


@api_view(["GET"])
def models_for_make(request, make):
    qs = VehicleModel.objects.filter(make__slug=make).select_related("make")
    return _cached(request, [s.model_dict(m) for m in qs])


@api_view(["GET"])
def generations_for_model(request, model):
    qs = VehicleGeneration.objects.filter(model__slug=model)
    return _cached(request, [s.generation_dict(g) for g in qs])


@api_view(["GET"])
def trims_for_generation(request, gen):
    qs = VehicleTrim.objects.filter(generation__slug=gen)
    return _cached(request, [s.trim_dict(t) for t in qs])


@api_view(["GET"])
def engines_for_generation(request, gen):
    qs = VehicleEngine.objects.filter(generation__slug=gen)
    return _cached(request, [s.engine_dict(e) for e in qs])


@api_view(["GET"])
def groups_for_generation(request, gen):
    """Storefront links for a generation hub page (one per VariantGroup)."""
    qs = (
        VariantGroup.objects.filter(generation__slug=gen)
        .select_related("trim", "generation")
        .order_by("-product_count")
    )
    data = [
        {
            "name": (g.trim.name if g.trim_id else "All trims"),
            "years": g.slug_years,
            "path": g.canonical_path,
            "product_count": g.product_count,
        }
        for g in qs
    ]
    return _cached(request, data)


@api_view(["GET"])
def resolve_vehicle(request):
    """Selector output → { canonical_url, group_id, product_count, ... }."""
    q = request.query_params
    variants = VehicleVariant.objects.filter(is_active=True).select_related(
        "generation__model__make", "trim", "engine"
    )
    if q.get("make"):
        variants = variants.filter(generation__model__make__slug=q["make"])
    if q.get("model"):
        variants = variants.filter(generation__model__slug=q["model"])
    if q.get("generation"):
        variants = variants.filter(generation__slug=q["generation"])
    if q.get("trim"):
        variants = variants.filter(trim__slug=q["trim"])
    if q.get("engine"):
        variants = variants.filter(engine__slug=q["engine"])
    if q.get("year"):
        try:
            year = int(q["year"])
            variants = variants.filter(year_from__lte=year, year_to__gte=year)
        except ValueError:
            pass

    variant = variants.first()
    if not variant:
        return Response({"detail": "No matching vehicle."}, status=404)
    group = variant.groups.first()
    return _cached(
        request,
        {
            "variant_id": variant.id,
            "group_id": group.id if group else None,
            "canonical_url": group.canonical_path if group else None,
            "display_name": variant.display_name,
            "product_count": group.product_count if group else 0,
        },
    )


# --------------------------------------------------------------------------
# THE endpoint — /api/v1/page/?path=/car-parts/.../
# --------------------------------------------------------------------------

@api_view(["GET"])
def page(request):
    path = request.query_params.get("path", "")
    if not path.endswith("/"):
        path += "/"
    page_num = max(int(request.query_params.get("page", "1") or 1), 1)
    brand_filter = request.query_params.get("brand", "")

    seo_page = (
        SeoPage.objects.filter(path=path)
        .select_related("variant_group__generation__model__make", "variant_group__trim", "category")
        .first()
    )
    if seo_page is None:
        return Response({"detail": "Not found."}, status=404)
    if seo_page.directive == "410":
        return Response({"detail": "Gone."}, status=410)

    cache_key = f"page:{path}:{page_num}:{brand_filter}"
    cached_body = cache.get(cache_key)
    if cached_body is not None:
        return _cached(request, cached_body)

    if seo_page.kind in ("vehicle", "vehicle_category"):
        body = _vehicle_page(seo_page, page_num, brand_filter)
    else:
        body = {"seo": s.seo_block(seo_page), "kind": seo_page.kind, "products": []}
    cache.set(cache_key, body, CACHE_TTL)
    return _cached(request, body)


def _vehicle_page(seo_page, page_num, brand_filter):
    group = seo_page.variant_group
    gen = group.generation
    variant_ids = list(group.variants.values_list("id", flat=True))

    idx = FitmentIndex.objects.filter(variant_id__in=variant_ids)
    if seo_page.kind == "vehicle_category":
        idx = idx.filter(category=seo_page.category)
    product_ids = set(idx.values_list("product_id", flat=True))

    products_q = Q(id__in=product_ids)
    universal_q = Q(is_universal=True)
    if seo_page.kind == "vehicle_category":
        universal_q &= Q(category=seo_page.category)
    products = (
        Product.objects.filter(products_q | universal_q, is_active=True)
        .select_related("brand", "offer")
        .prefetch_related("images")
        .order_by("-offer__availability", "name")
    )
    if brand_filter:
        products = products.filter(brand__slug=brand_filter)

    total = products.count()
    start = (page_num - 1) * PAGE_SIZE
    page_products = list(products[start : start + PAGE_SIZE])

    # Facets straight off the denormalised index — one query each.
    brand_facets = list(
        FitmentIndex.objects.filter(variant_id__in=variant_ids)
        .values("brand__name", "brand__slug")
        .annotate(count=Count("product", distinct=True))
        .order_by("-count")[:20]
    )
    category_tiles = list(
        FitmentIndex.objects.filter(variant_id__in=variant_ids, product__is_active=True)
        .values("category__name", "category__slug")
        .annotate(count=Count("product", distinct=True))
        .order_by("-count")[:12]
    )

    vehicle_bits = [gen.model.make.name, gen.model.name, gen.code]
    if group.trim_id:
        vehicle_bits.append(group.trim.name)
    vehicle_name = " ".join(vehicle_bits)

    breadcrumbs = [
        {"name": "Home", "path": "/"},
        {"name": gen.model.make.name, "path": f"/car-parts/{gen.model.make.slug}/"},
        {"name": gen.model.name, "path": f"/car-parts/{gen.model.make.slug}/{gen.model.slug}/"},
        {"name": gen.code, "path": f"/car-parts/{gen.model.make.slug}/{gen.model.slug}/{gen.slug}/"},
        {"name": group.slug_years, "path": group.canonical_path},
    ]
    if seo_page.kind == "vehicle_category":
        breadcrumbs.append({"name": seo_page.category.name, "path": seo_page.path})

    # Internal-linking blocks — SEO gold, all from data we already have.
    other_trims = [
        {"name": (g.trim.name if g.trim_id else "All trims"), "path": g.canonical_path}
        for g in VariantGroup.objects.filter(generation=gen)
        .exclude(id=group.id)
        .select_related("trim")[:8]
    ]
    other_generations = [
        {"name": f"{g.code} ({g.year_display})", "path": f"/car-parts/{gen.model.make.slug}/{gen.model.slug}/{g.slug}/"}
        for g in VehicleGeneration.objects.filter(model=gen.model).exclude(id=gen.id)[:8]
    ]

    cards = [s.product_card(p) for p in page_products]
    structured = [
        sd.breadcrumbs_jsonld(breadcrumbs),
        sd.itemlist_jsonld(cards, seo_page.path),
        sd.faq_jsonld(vehicle_name, [c["category__name"] for c in category_tiles]),
    ]

    return {
        "kind": seo_page.kind,
        "seo": s.seo_block(seo_page),
        "hero": {
            "vehicle_name": vehicle_name,
            "years": group.slug_years,
            "product_count": total,
        },
        "breadcrumbs": breadcrumbs,
        "category_tiles": [
            {"name": c["category__name"], "slug": c["category__slug"], "count": c["count"],
             "path": f"{group.canonical_path}{c['category__slug']}/"}
            for c in category_tiles
        ],
        "products": cards,
        "facets": {
            "brands": [
                {"name": b["brand__name"], "slug": b["brand__slug"], "count": b["count"]}
                for b in brand_facets
            ]
        },
        "pagination": {
            "page": page_num,
            "page_size": PAGE_SIZE,
            "total": total,
            "pages": max((total + PAGE_SIZE - 1) // PAGE_SIZE, 1),
        },
        "related_links": {
            "other_trims": other_trims,
            "other_generations": other_generations,
            "popular_categories": [
                {"name": c["category__name"], "path": f"{group.canonical_path}{c['category__slug']}/"}
                for c in category_tiles[:6]
            ],
        },
        "structured_data": structured,
    }


# --------------------------------------------------------------------------
# Category browsing (parts by category + general catalog: laptops, phones)
# --------------------------------------------------------------------------

@api_view(["GET"])
def categories(request):
    """Root categories with product counts (descendants included). Cached 1h."""
    cache_key = "api:categories:v1"
    body = cache.get(cache_key)
    if body is None:
        roots = Category.get_root_nodes()
        body = []
        for root in roots:
            descendant_ids = [root.id] + [c.id for c in root.get_descendants()]
            count = Product.objects.filter(
                category_id__in=descendant_ids, is_active=True
            ).count()
            body.append({
                "name": root.name,
                "slug": root.slug,
                "kind": root.kind,
                "product_count": count,
                "children": [
                    {"name": c.name, "slug": c.slug} for c in root.get_children()[:10]
                ],
            })
        cache.set(cache_key, body, CACHE_TTL)
    return _cached(request, body)


@api_view(["GET"])
def shop_category(request, slug):
    """Browse a category (and its descendants): parts or general goods."""
    category = Category.objects.filter(slug=slug).first()
    if category is None:
        return Response({"detail": "Not found."}, status=404)
    page_num = max(int(request.query_params.get("page", "1") or 1), 1)

    descendant_ids = [category.id] + [c.id for c in category.get_descendants()]
    products = (
        Product.objects.filter(category_id__in=descendant_ids, is_active=True)
        .select_related("brand", "offer")
        .prefetch_related("images")
        .order_by("-offer__availability", "name")
    )
    total = products.count()
    start = (page_num - 1) * PAGE_SIZE
    cards = [s.product_card(p) for p in products[start : start + PAGE_SIZE]]

    ancestors = [{"name": a.name, "slug": a.slug} for a in category.get_ancestors()]
    children = [
        {"name": c.name, "slug": c.slug} for c in category.get_children()
    ]
    return _cached(request, {
        "category": {
            "name": category.name,
            "slug": category.slug,
            "kind": category.kind,
            "description": category.description,
            "seo_title": category.seo_title or f"{category.name} in Kenya | Corporation Premium",
            "seo_description": category.seo_description,
        },
        "ancestors": ancestors,
        "children": children,
        "products": cards,
        "pagination": {
            "page": page_num,
            "page_size": PAGE_SIZE,
            "total": total,
            "pages": max((total + PAGE_SIZE - 1) // PAGE_SIZE, 1),
        },
    })


# --------------------------------------------------------------------------
# Products
# --------------------------------------------------------------------------

@api_view(["GET"])
def product_detail(request, slug):
    p = (
        Product.objects.filter(slug=slug, is_active=True)
        .select_related("brand", "category", "offer")
        .prefetch_related("images", "part_numbers")
        .first()
    )
    if p is None:
        return Response({"detail": "Not found."}, status=404)

    fits = (
        FitmentIndex.objects.filter(product=p)
        .select_related("variant__generation__model__make", "variant__trim", "variant__engine")[:200]
    )
    fits_rows, also_fits, seen_groups = [], [], set()
    for fi in fits:
        v = fi.variant
        fits_rows.append({
            "vehicle": v.display_name,
            "position": fi.position,
            "years": f"{v.year_from}–{'present' if v.year_to == 9999 else v.year_to}",
        })
        group = v.groups.first()
        if group and group.id not in seen_groups and len(also_fits) < 10:
            seen_groups.add(group.id)
            also_fits.append({"name": v.display_name, "path": group.canonical_path})

    fits_names = [r["vehicle"] for r in fits_rows]
    body = {
        "product": {
            **s.product_card(p),
            "description": p.description,
            "specs": p.specs,
            "gtin": p.gtin,
            "category": p.category.name,
            "category_slug": p.category.slug,
            "is_universal": p.is_universal,
            "images": [s._media(img.image) for img in p.images.all() if img.image],
            "part_numbers": [
                {"number": pn.number, "kind": pn.kind} for pn in p.part_numbers.all()
            ],
        },
        "fits_summary": fits_rows[:8],
        "fits_count": FitmentIndex.objects.filter(product=p).count(),
        "also_fits": also_fits,
        "structured_data": [sd.product_jsonld(p, fits_names)],
    }
    return _cached(request, body)


@api_view(["GET"])
def product_fits(request, slug):
    """Paginated 'Fits these vehicles' table."""
    page_num = max(int(request.query_params.get("page", "1") or 1), 1)
    qs = (
        FitmentIndex.objects.filter(product__slug=slug)
        .select_related("variant__generation__model__make", "variant__trim", "variant__engine")
        .order_by("variant__generation__model__make__name", "variant__year_from")
    )
    total = qs.count()
    start = (page_num - 1) * 50
    rows = [
        {
            "vehicle": fi.variant.display_name,
            "position": fi.position,
        }
        for fi in qs[start : start + 50]
    ]
    return _cached(request, {"rows": rows, "total": total, "page": page_num})


# --------------------------------------------------------------------------
# Search — a router into the SEO pages
# --------------------------------------------------------------------------

@api_view(["GET"])
def search(request):
    q = request.query_params.get("q", "").strip()
    if not q:
        return Response({"results": []})

    # 1. Part-number fast path: exact normalized hit → 302 to the product.
    product = part_number_lookup(q)
    if product:
        return Response({"redirect_to": f"/products/{product.slug}/"})

    # 2. Vehicle intent: "prado 2018 brake pads" → the SEO storefront URL.
    intent = parse_vehicle_intent(q)
    if intent:
        variants = VehicleVariant.objects.filter(
            is_active=True, generation__model=intent["model"]
        )
        if intent["year"]:
            variants = variants.filter(
                year_from__lte=intent["year"], year_to__gte=intent["year"]
            )
        variant = variants.first()
        group = variant.groups.first() if variant else None
        if group:
            target = group.canonical_path
            if intent["category"]:
                target = f"{target}{intent['category'].slug}/"
            if SeoPage.objects.filter(path=target).exists():
                return Response({"redirect_to": target})
            return Response({"redirect_to": group.canonical_path})

    # 3. Text search.
    results = [s.product_card(p) for p in text_search(q)]
    return Response({"results": results, "query": q})


@api_view(["GET"])
def seo_changed(request):
    """Paths to revalidate — the frontend cron pulls this."""
    since = request.query_params.get("since")
    qs = SeoPage.objects.all()
    if since:
        parsed = timezone.datetime.fromisoformat(since)
        if timezone.is_naive(parsed):
            parsed = timezone.make_aware(parsed)
        qs = qs.filter(last_computed__gte=parsed)
    return Response({"paths": list(qs.values_list("path", flat=True)[:500])})
