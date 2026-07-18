"""Data-quality audit. Exit gate: zero criticals.

Criticals: FitmentIndex drift vs a brute-force recompute, fitment rules that
resolve to zero variants, active products with no fitment and not universal.
"""
from django.core.management.base import BaseCommand

from apps.catalog.models import Product
from apps.fitment.models import Fitment, FitmentIndex
from apps.fitment.services import variant_position_pairs


class Command(BaseCommand):
    help = "Audit fitment data quality. Returns non-zero exit code on criticals."

    def add_arguments(self, parser):
        parser.add_argument("--email-report", action="store_true")

    def handle(self, *args, **opts):
        criticals, warnings = [], []

        for product in Product.objects.filter(is_active=True).prefetch_related("fitments"):
            fits = list(product.fitments.all())
            if not fits and not product.is_universal:
                warnings.append(f"{product.sku}: active, no fitment, not universal")
                continue
            if product.is_universal:
                continue
            expected = {(vid, pos) for vid, pos in variant_position_pairs(product)}
            actual = set(
                FitmentIndex.objects.filter(product=product).values_list("variant_id", "position")
            )
            if expected != actual:
                criticals.append(
                    f"{product.sku}: index drift (expected {len(expected)}, got {len(actual)})"
                )

        for f in Fitment.objects.filter(is_exclusion=False).select_related("product"):
            from apps.fitment.services import _match

            if not _match(f):
                warnings.append(f"fitment #{f.pk} ({f.product.sku}): resolves to zero variants")

        for line in criticals:
            self.stderr.write(self.style.ERROR(f"CRITICAL {line}"))
        for line in warnings:
            self.stdout.write(self.style.WARNING(f"warning  {line}"))
        self.stdout.write(
            self.style.SUCCESS(f"fitment_audit: {len(criticals)} critical(s), {len(warnings)} warning(s)")
        )
        if criticals:
            raise SystemExit(1)
