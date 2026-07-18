from django.core.management.base import BaseCommand

from apps.seo.groups import build_all_groups


class Command(BaseCommand):
    help = "Collapse variants by product-set fingerprint into VariantGroups. Nightly, idempotent."

    def handle(self, *args, **opts):
        n = build_all_groups()
        self.stdout.write(self.style.SUCCESS(f"build_variant_groups: {n} group(s)"))
