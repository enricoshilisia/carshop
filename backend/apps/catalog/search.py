"""Search: part-number fast path, vehicle-intent parsing, then text search.

MySQL gets FULLTEXT (ngram) via a vendor-gated raw migration; everywhere
else falls back to icontains capped at 50 rows. Ugly, works, costs nothing.
"""
import re

from django.db import connection

from apps.catalog.models import PartNumber, Product, ProductSearchDoc, normalize_part_number


def rebuild_search_doc(product: Product) -> None:
    parts = [
        product.name,
        product.brand.name,
        product.mpn,
        product.sku,
        product.category.name,
        product.description[:500],
        " ".join(pn.number for pn in product.part_numbers.all()),
    ]
    text = " ".join(p for p in parts if p)
    ProductSearchDoc.objects.update_or_create(product=product, defaults={"text": text})


def part_number_lookup(q: str) -> Product | None:
    """A mechanic typing 04465-60280 must land on the right page. One query."""
    normalized = normalize_part_number(q)
    if len(normalized) < 4:
        return None
    hit = (
        PartNumber.objects.filter(normalized=normalized, product__is_active=True)
        .select_related("product")
        .first()
    )
    return hit.product if hit else None


def text_search(q: str, limit: int = 50) -> list[Product]:
    q = q.strip()
    if not q:
        return []
    if connection.vendor == "mysql":
        docs = ProductSearchDoc.objects.raw(
            "SELECT id, product_id FROM catalog_productsearchdoc "
            "WHERE MATCH(text) AGAINST (%s IN BOOLEAN MODE) LIMIT %s",
            [q, limit],
        )
        ids = [d.product_id for d in docs]
        products = Product.objects.filter(id__in=ids, is_active=True).select_related("brand", "offer")
        by_id = {p.id: p for p in products}
        return [by_id[i] for i in ids if i in by_id]
    # Portable fallback.
    return list(
        Product.objects.filter(is_active=True, search_doc__text__icontains=q)
        .select_related("brand", "offer")[:limit]
    )


_YEAR_RE = re.compile(r"\b(19[5-9]\d|20[0-4]\d)\b")


def parse_vehicle_intent(q: str) -> dict | None:
    """'prado 2018 brake pads' → storefront redirect parts.

    Matches make/model names + aliases and category names against the
    query words; returns None when no vehicle is recognised.
    """
    from apps.catalog.models import Category
    from apps.vehicles.models import VehicleModel, VehicleModelAlias

    q_lower = f" {q.lower()} "
    year = None
    m = _YEAR_RE.search(q)
    if m:
        year = int(m.group(0))

    model = None
    for alias in VehicleModelAlias.objects.select_related("model__make"):
        if f" {alias.alias.lower()} " in q_lower:
            model = alias.model
            break
    if model is None:
        for vm in VehicleModel.objects.select_related("make"):
            if f" {vm.name.lower()} " in q_lower or f" {vm.slug.replace('-', ' ')} " in q_lower:
                model = vm
                break
    if model is None:
        return None

    category = None
    for cat in Category.objects.filter(kind="vehicle"):
        if f" {cat.name.lower()} " in q_lower or f" {cat.slug.replace('-', ' ')} " in q_lower:
            category = cat
            break

    return {"model": model, "year": year, "category": category}
