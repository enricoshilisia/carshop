"""Fitment resolution — Fitment rules → flattened FitmentIndex edges.

Inclusion rules are matched against variants with a portable, index-friendly
year-overlap test (a1 <= b2 AND b1 <= a2 — no Postgres ranges), then
exclusion rules are subtracted.
"""
from collections import defaultdict

from django.db import transaction

from apps.fitment.models import Fitment, FitmentIndex
from apps.vehicles.models import VehicleVariant


def _match(f: Fitment) -> set[int]:
    qs = VehicleVariant.objects.filter(
        is_active=True,
        generation_id=f.generation_id,
        year_from__lte=f.year_to,
        year_to__gte=f.year_from,
    )
    if f.trim_id:
        qs = qs.filter(trim_id=f.trim_id)
    if f.engine_id:
        qs = qs.filter(engine_id=f.engine_id)
    if f.drivetrain:
        qs = qs.filter(drivetrain=f.drivetrain)
    return set(qs.values_list("id", flat=True))


def resolve_variants(product) -> set[int]:
    """All active variant ids this product fits. Universal parts match everything."""
    if product.is_universal:
        return set(VehicleVariant.objects.filter(is_active=True).values_list("id", flat=True))

    fits = list(product.fitments.all())
    included: set[int] = set()
    excluded: set[int] = set()
    for f in fits:
        (excluded if f.is_exclusion else included).update(_match(f))
    return included - excluded


def variant_position_pairs(product) -> list[tuple[int, str]]:
    """(variant_id, position) pairs after exclusion subtraction.

    A variant can appear once per distinct position (front + rear pads on
    the same car are two rows, by design of the unique constraint).
    """
    fits = list(product.fitments.all())
    excluded: set[int] = set()
    positions: dict[int, set[str]] = defaultdict(set)

    for f in fits:
        if f.is_exclusion:
            excluded.update(_match(f))
    for f in fits:
        if f.is_exclusion:
            continue
        for vid in _match(f):
            positions[vid].add(f.position or "")

    return [
        (vid, pos)
        for vid, pos_set in positions.items()
        if vid not in excluded
        for pos in pos_set
    ]


def rebuild_product_index(product) -> int:
    """Fast (<50ms typical). Runs INLINE on Product/Fitment save — no queue needed.

    Universal products are NOT materialised (50k rows per SKU); the API
    UNIONs them in with Q(is_universal=True) at query time.
    """
    with transaction.atomic():
        FitmentIndex.objects.filter(product=product).delete()
        if product.is_universal or not product.is_active:
            return 0
        rows = [
            FitmentIndex(
                product=product,
                variant_id=vid,
                category_id=product.category_id,
                brand_id=product.brand_id,
                position=pos,
            )
            for vid, pos in variant_position_pairs(product)
        ]
        FitmentIndex.objects.bulk_create(rows, batch_size=500, ignore_conflicts=True)
        return len(rows)


def rebuild_generation(generation_id: int, product_ids: list[int] | None = None, chunk: int = 200):
    """Rebuild the index for every product with a fitment on this generation.

    Called from the Job queue (a variant/generation edit touches every
    product on the generation — too much for inline). Returns the list of
    product ids still to do, so the job handler can checkpoint + re-queue.
    """
    from apps.catalog.models import Product

    if product_ids is None:
        product_ids = sorted(
            Fitment.objects.filter(generation_id=generation_id)
            .values_list("product_id", flat=True)
            .distinct()
        )
    now, later = product_ids[:chunk], product_ids[chunk:]
    for product in Product.objects.filter(id__in=now):
        rebuild_product_index(product)
    return later
