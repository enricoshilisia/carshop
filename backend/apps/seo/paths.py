"""Canonical URL construction — ONE place builds storefront paths."""
from apps.vehicles.models import VariantGroup


def group_path(group: VariantGroup) -> str:
    gen = group.generation
    bits = ["", "car-parts", gen.model.make.slug, gen.model.slug, gen.slug]
    if group.trim_id:
        bits.append(group.trim.slug)
    bits.append(group.slug_years)
    return "/".join(bits) + "/"


def group_category_path(group: VariantGroup, category_slug: str) -> str:
    return f"{group_path(group)}{category_slug}/"


def product_path(product) -> str:
    return f"/products/{product.slug}/"
