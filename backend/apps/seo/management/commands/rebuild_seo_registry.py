from django.core.management.base import BaseCommand

from apps.seo.rules import rebuild_registry


class Command(BaseCommand):
    help = "Run the SEO rule engine over every group/category/product. Nightly, idempotent."

    def handle(self, *args, **opts):
        stats = rebuild_registry()
        self.stdout.write(self.style.SUCCESS(f"rebuild_seo_registry: {stats}"))
