"""Google Merchant Center XML feed written to disk by cron.

GMC fetches /static/feeds/google-shopping.xml on its own schedule — zero
origin CPU at fetch time, served by Cloudflare. --delta writes a small
supplemental feed with recently-changed offers only.
"""
from datetime import timedelta
from xml.sax.saxutils import escape

from django.conf import settings
from django.core.management.base import BaseCommand
from django.utils import timezone

from apps.catalog.models import Product
from apps.fitment.models import FitmentIndex

G_AVAILABILITY = {
    "in_stock": "in stock",
    "out_of_stock": "out of stock",
    "preorder": "preorder",
    "backorder": "backorder",
}


class Command(BaseCommand):
    help = "Write the Google Shopping XML feed (also reusable for Facebook/Jiji)."

    def add_arguments(self, parser):
        parser.add_argument("--delta", action="store_true", help="Only offers changed in the last hour")
        parser.add_argument("--full", action="store_true")

    def handle(self, *args, **opts):
        out = settings.FEED_DIR
        out.mkdir(parents=True, exist_ok=True)

        qs = (
            Product.objects.filter(is_active=True, offer__isnull=False)
            .select_related("brand", "category", "offer")
            .prefetch_related("images")
        )
        filename = "google-shopping.xml"
        if opts["delta"] and not opts["full"]:
            qs = qs.filter(offer__updated_at__gte=timezone.now() - timedelta(hours=1))
            filename = "google-shopping-delta.xml"

        items = []
        for p in qs.iterator(chunk_size=500):
            items.append(self._item(p))
        body = "\n".join(items)
        (out / filename).write_text(
            '<?xml version="1.0" encoding="UTF-8"?>\n'
            '<rss version="2.0" xmlns:g="http://base.google.com/ns/1.0">\n'
            "<channel>\n"
            "<title>Corporation Premium</title>\n"
            f"<link>{escape(settings.SITE_BASE_URL)}</link>\n"
            "<description>Car parts by vehicle fitment, Kenya</description>\n"
            f"{body}\n"
            "</channel>\n</rss>\n",
            encoding="utf-8",
        )
        self.stdout.write(self.style.SUCCESS(f"sync_merchant_feed: {len(items)} item(s) -> {filename}"))

    def _item(self, p: Product) -> str:
        offer = p.offer
        link = f"{settings.SITE_BASE_URL}/products/{p.slug}/"
        top_fit = (
            FitmentIndex.objects.filter(product=p)
            .select_related("variant__generation__model__make", "variant__trim")
            .first()
        )
        top_vehicle = top_fit.variant.display_name if top_fit else ""
        title = f"{p.brand.name} {p.name}"
        if top_vehicle:
            title = f"{title} — Fits {top_vehicle}"
        title = title[:150]
        description = p.description or p.name
        if top_vehicle:
            description = f"{description} Verified fitment for {top_vehicle}."
        images = [img for img in p.images.all() if img.image]
        make_label = ""
        if top_fit:
            make_label = top_fit.variant.generation.model.make.slug

        def tag(name, value):
            return f"<{name}>{escape(str(value))}</{name}>" if value not in ("", None) else ""

        fields = [
            tag("g:id", p.sku),
            tag("title", title),
            tag("description", description[:5000]),
            tag("link", link),
            tag("g:image_link", f"{settings.API_BASE_URL}{images[0].image.url}") if images else "",
            "".join(
                tag("g:additional_image_link", f"{settings.API_BASE_URL}{img.image.url}")
                for img in images[1:11]
            ),
            tag("g:availability", G_AVAILABILITY.get(offer.availability, "in stock")),
            tag("g:price", f"{offer.price} {offer.currency}"),
            tag("g:sale_price", f"{offer.compare_at} {offer.currency}") if offer.compare_at else "",
            tag("g:brand", p.brand.name),
            tag("g:gtin", p.gtin),
            tag("g:mpn", p.mpn),
            tag("g:identifier_exists", "false") if not p.gtin and not p.mpn else "",
            tag("g:condition", p.condition),
            tag("g:google_product_category", p.category.google_category),
            tag("g:product_type", " > ".join(a.name for a in p.category.get_ancestors()) or p.category.name),
            tag("g:shipping_weight", f"{p.weight_kg} kg") if p.weight_kg else "",
            # custom_label_0 = make lets you bid Toyota vs Mercedes separately later.
            tag("g:custom_label_0", make_label),
        ]
        return "<item>" + "".join(f for f in fields if f) + "</item>"
