"""VariantGroup builder — the anti-duplicate weapon.

Variants sharing an IDENTICAL resolved product set (sha256 fingerprint of the
sorted product-id list) collapse into ONE group → one canonical URL. Prado TX
2018 and Prado TX 2019 with the same parts become one page. This is how you
publish ~8,000 strong pages instead of 750,000 thin ones.
"""
import hashlib

from django.db import transaction

from apps.fitment.models import FitmentIndex
from apps.seo import paths
from apps.vehicles.models import OPEN_YEAR, VehicleGeneration, VehicleVariant, VariantGroup


def _fingerprint(product_ids: list[int]) -> str:
    return hashlib.sha256(",".join(map(str, sorted(product_ids))).encode()).hexdigest()


def _slug_years(year_from: int, year_to: int) -> str:
    return f"{year_from}-{'present' if year_to == OPEN_YEAR else year_to}"


def build_groups_for_generation(generation: VehicleGeneration) -> int:
    """Idempotent: recomputes the generation's groups from FitmentIndex."""
    variants = list(generation.variants.filter(is_active=True))
    if not variants:
        VariantGroup.objects.filter(generation=generation).delete()
        return 0

    products_by_variant: dict[int, set[int]] = {v.id: set() for v in variants}
    for pid, vid in FitmentIndex.objects.filter(
        variant__generation=generation, product__is_active=True
    ).values_list("product_id", "variant_id"):
        products_by_variant.setdefault(vid, set()).add(pid)

    buckets: dict[str, list[VehicleVariant]] = {}
    fingerprints: dict[str, list[int]] = {}
    for v in variants:
        pids = sorted(products_by_variant.get(v.id, set()))
        fp = _fingerprint(pids)
        buckets.setdefault(fp, []).append(v)
        fingerprints[fp] = pids

    with transaction.atomic():
        VariantGroup.objects.filter(generation=generation).delete()
        created = 0
        for fp, members in buckets.items():
            trims = {m.trim_id for m in members}
            engines = {m.engine_id for m in members}
            group = VariantGroup(
                generation=generation,
                trim_id=trims.pop() if len(trims) == 1 else None,
                engine_id=engines.pop() if len(engines) == 1 else None,
                year_from=min(m.year_from for m in members),
                year_to=max(m.year_to for m in members),
                fingerprint=fp,
                product_count=len(fingerprints[fp]),
            )
            group.slug_years = _slug_years(group.year_from, group.year_to)
            group.canonical_path = paths.group_path(group)
            # Two fingerprints can collide on the same URL (e.g. trim-less
            # buckets with different part sets). Disambiguate deterministically.
            if VariantGroup.objects.filter(canonical_path=group.canonical_path).exists():
                group.canonical_path = group.canonical_path.rstrip("/") + f"-{fp[:6]}/"
            group.save()
            group.variants.set(members)
            created += 1
    return created


def build_all_groups() -> int:
    total = 0
    for gen in VehicleGeneration.objects.select_related("model__make").all():
        total += build_groups_for_generation(gen)
    return total
