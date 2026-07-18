"""Lean dict shapers — aggressively shaped for the frontend, one page one call."""
from django.conf import settings


def _media(url_or_field):
    if not url_or_field:
        return None
    return f"{settings.API_BASE_URL}{url_or_field.url}"


def product_card(p, primary_image=None) -> dict:
    offer = getattr(p, "offer", None)
    img = primary_image
    if img is None:
        images = list(p.images.all())
        img = images[0] if images else None
    return {
        "id": p.id,
        "slug": p.slug,
        "name": p.name,
        "brand": p.brand.name,
        "sku": p.sku,
        "mpn": p.mpn,
        "condition": p.condition,
        "url": f"/products/{p.slug}/",
        "image": _media(img.image) if img else None,
        "price": str(offer.price) if offer else None,
        "compare_at": str(offer.compare_at) if offer and offer.compare_at else None,
        "currency": offer.currency if offer else "KES",
        "availability": offer.availability if offer else None,
        "in_stock": bool(offer and offer.availability == "in_stock"),
    }


def seo_block(page) -> dict:
    return {
        "title": page.title,
        "meta_description": page.meta_description,
        "h1": page.h1,
        "canonical": page.canonical_to or page.path,
        "directive": page.directive,
        "intro_html": page.intro_html,
    }


def make_dict(m) -> dict:
    return {"id": m.id, "name": m.name, "slug": m.slug, "logo": _media(m.logo)}


def model_dict(vm) -> dict:
    return {"id": vm.id, "name": vm.name, "slug": vm.slug, "make": vm.make.slug}


def generation_dict(g) -> dict:
    return {
        "id": g.id,
        "code": g.code,
        "slug": g.slug,
        "year_from": g.year_from,
        "year_to": g.year_to,
        "year_display": g.year_display,
        "body_type": g.body_type,
    }


def trim_dict(t) -> dict:
    return {"id": t.id, "name": t.name, "slug": t.slug}


def engine_dict(e) -> dict:
    return {
        "id": e.id,
        "display": e.display,
        "code": e.code,
        "slug": e.slug,
        "fuel": e.fuel,
        "capacity_cc": e.capacity_cc,
    }
