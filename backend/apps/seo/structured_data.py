"""JSON-LD generated in Django, injected as-is by Next.js.

Never build schema in the frontend — the moment it lives in two places it
drifts, and Google reads the drift, not your intent.
"""
from datetime import date, timedelta

from django.conf import settings

AVAILABILITY_SCHEMA = {
    "in_stock": "https://schema.org/InStock",
    "out_of_stock": "https://schema.org/OutOfStock",
    "preorder": "https://schema.org/PreOrder",
    "backorder": "https://schema.org/BackOrder",
}
CONDITION_SCHEMA = {
    "new": "https://schema.org/NewCondition",
    "used": "https://schema.org/UsedCondition",
    "refurbished": "https://schema.org/RefurbishedCondition",
}


def _abs(path: str) -> str:
    return f"{settings.SITE_BASE_URL}{path}"


def product_jsonld(product, fits_names: list[str]) -> dict:
    offer = getattr(product, "offer", None)
    images = [
        f"{settings.API_BASE_URL}{img.image.url}" for img in product.images.all() if img.image
    ]
    data = {
        "@context": "https://schema.org",
        "@type": "Product",
        "name": product.name,
        "sku": product.sku,
        "brand": {"@type": "Brand", "name": product.brand.name},
    }
    if product.mpn:
        data["mpn"] = product.mpn
    if product.gtin:
        data["gtin"] = product.gtin
    if images:
        data["image"] = images
    if product.description:
        data["description"] = product.description[:5000]
    if fits_names:
        # The fitment signal Google reads.
        data["isAccessoryOrSparePartFor"] = [
            {"@type": "Product", "name": n} for n in fits_names[:20]
        ]
    if offer:
        data["offers"] = {
            "@type": "Offer",
            "priceCurrency": offer.currency,
            "price": str(offer.price),
            "availability": AVAILABILITY_SCHEMA.get(offer.availability),
            "itemCondition": CONDITION_SCHEMA.get(product.condition),
            "url": _abs(f"/products/{product.slug}/"),
            "priceValidUntil": (date.today() + timedelta(days=90)).isoformat(),
        }
    # NOTE: aggregateRating ONLY when real reviews exist. Faking it = Merchant suspension.
    return data


def breadcrumbs_jsonld(crumbs: list[dict]) -> dict:
    return {
        "@context": "https://schema.org",
        "@type": "BreadcrumbList",
        "itemListElement": [
            {
                "@type": "ListItem",
                "position": i + 1,
                "name": c["name"],
                "item": _abs(c["path"]),
            }
            for i, c in enumerate(crumbs)
        ],
    }


def itemlist_jsonld(products: list[dict], path: str) -> dict:
    return {
        "@context": "https://schema.org",
        "@type": "ItemList",
        "url": _abs(path),
        "numberOfItems": len(products),
        "itemListElement": [
            {"@type": "ListItem", "position": i + 1, "url": _abs(p["url"])}
            for i, p in enumerate(products)
        ],
    }


def faq_jsonld(vehicle_name: str, category_names: list[str]) -> dict:
    faqs = [
        {
            "@type": "Question",
            "name": f"What {cat.lower()} fit a {vehicle_name}?",
            "acceptedAnswer": {
                "@type": "Answer",
                "text": (
                    f"Corporation Premium stocks {cat.lower()} with verified fitment for the "
                    f"{vehicle_name}. Every part listed on this page has been checked against "
                    "the exact generation, trim and year range, with delivery across Kenya."
                ),
            },
        }
        for cat in category_names[:4]
    ]
    return {"@context": "https://schema.org", "@type": "FAQPage", "mainEntity": faqs}


def organization_jsonld() -> dict:
    return {
        "@context": "https://schema.org",
        "@type": "Organization",
        "name": "Corporation Premium",
        "url": settings.SITE_BASE_URL,
    }


def website_jsonld() -> dict:
    return {
        "@context": "https://schema.org",
        "@type": "WebSite",
        "name": "Corporation Premium",
        "url": settings.SITE_BASE_URL,
        "potentialAction": {
            "@type": "SearchAction",
            "target": f"{settings.SITE_BASE_URL}/search?q={{search_term_string}}",
            "query-input": "required name=search_term_string",
        },
    }
