"""Static XML sitemaps written to disk by cron — NEVER generated per request.

Shards of ≤45,000 URLs, only directive=index rows, real lastmod.
"""
from xml.sax.saxutils import escape

from django.conf import settings
from django.core.management.base import BaseCommand

from apps.seo.models import SeoPage


class Command(BaseCommand):
    help = "Write static sitemap shards + index to SITEMAP_DIR."

    def handle(self, *args, **opts):
        out = settings.SITEMAP_DIR
        out.mkdir(parents=True, exist_ok=True)
        pages = SeoPage.objects.filter(directive="index").order_by("-priority", "path")
        shard_size = settings.SITEMAP_SHARD_SIZE
        shards = []
        batch = []
        for page in pages.iterator(chunk_size=2000):
            batch.append(page)
            if len(batch) >= shard_size:
                shards.append(batch)
                batch = []
        if batch:
            shards.append(batch)

        for i, shard in enumerate(shards, start=1):
            rows = "\n".join(
                "  <url><loc>{}</loc><lastmod>{}</lastmod><priority>{:.1f}</priority></url>".format(
                    escape(f"{settings.SITE_BASE_URL}{p.path}"),
                    p.last_computed.date().isoformat(),
                    p.priority,
                )
                for p in shard
            )
            (out / f"sitemap-{i}.xml").write_text(
                '<?xml version="1.0" encoding="UTF-8"?>\n'
                '<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">\n'
                f"{rows}\n</urlset>\n",
                encoding="utf-8",
            )

        index_rows = "\n".join(
            "  <sitemap><loc>{}</loc></sitemap>".format(
                escape(f"{settings.SITE_BASE_URL}/static/sitemaps/sitemap-{i}.xml")
            )
            for i in range(1, len(shards) + 1)
        )
        (out / "sitemap.xml").write_text(
            '<?xml version="1.0" encoding="UTF-8"?>\n'
            '<sitemapindex xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">\n'
            f"{index_rows}\n</sitemapindex>\n",
            encoding="utf-8",
        )
        total = sum(len(s) for s in shards)
        self.stdout.write(self.style.SUCCESS(f"build_sitemaps: {total} URL(s) in {len(shards)} shard(s)"))
