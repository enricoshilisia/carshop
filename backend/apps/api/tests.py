"""API contract + query-budget tests. ≤12 queries per endpoint — N+1 here is an outage."""
from django.core.cache import cache
from django.core.management import call_command
from django.test import TestCase

from apps.seo.models import SeoPage
from apps.vehicles.models import VariantGroup


class ApiFlowTests(TestCase):
    @classmethod
    def setUpTestData(cls):
        call_command("seed_demo")
        call_command("build_variant_groups")
        call_command("rebuild_seo_registry")

    def setUp(self):
        cache.clear()

    def test_makes_endpoint(self):
        resp = self.client.get("/api/v1/vehicles/makes/")
        self.assertEqual(resp.status_code, 200)
        slugs = [m["slug"] for m in resp.json()]
        self.assertIn("toyota", slugs)

    def test_selector_chain(self):
        models = self.client.get("/api/v1/vehicles/makes/toyota/models/").json()
        self.assertTrue(any(m["slug"] == "land-cruiser-prado" for m in models))
        gens = self.client.get("/api/v1/vehicles/models/land-cruiser-prado/generations/").json()
        self.assertTrue(any(g["slug"] == "j150" for g in gens))
        trims = self.client.get("/api/v1/vehicles/generations/j150/trims/").json()
        self.assertTrue(any(t["slug"] == "tx" for t in trims))

    def test_resolve_returns_canonical_url(self):
        resp = self.client.get(
            "/api/v1/vehicles/resolve/",
            {"make": "toyota", "model": "land-cruiser-prado", "generation": "j150", "year": 2018},
        )
        self.assertEqual(resp.status_code, 200)
        data = resp.json()
        self.assertTrue(data["canonical_url"].startswith("/car-parts/toyota/land-cruiser-prado/j150/"))
        self.assertGreater(data["product_count"], 0)

    def test_page_endpoint_vehicle_storefront(self):
        group = VariantGroup.objects.filter(product_count__gt=0).first()
        self.assertIsNotNone(group)
        resp = self.client.get("/api/v1/page/", {"path": group.canonical_path})
        self.assertEqual(resp.status_code, 200)
        body = resp.json()
        self.assertIn("seo", body)
        self.assertIn("products", body)
        self.assertGreater(len(body["products"]), 0)
        self.assertTrue(body["structured_data"])

    def test_page_endpoint_404_and_410(self):
        self.assertEqual(
            self.client.get("/api/v1/page/", {"path": "/car-parts/nonexistent/"}).status_code, 404
        )
        page = SeoPage.objects.filter(kind="vehicle").first()
        page.manual_override = True
        page.directive = "410"
        page.save()
        self.assertEqual(
            self.client.get("/api/v1/page/", {"path": page.path}).status_code, 410
        )

    def test_page_query_budget(self):
        """≤12 data queries (DatabaseCache bookkeeping queries excluded)."""
        from django.db import connection
        from django.test.utils import CaptureQueriesContext

        group = VariantGroup.objects.filter(product_count__gt=0).first()
        cache.clear()
        with CaptureQueriesContext(connection) as ctx:
            self.client.get("/api/v1/page/", {"path": group.canonical_path})
        data_queries = [
            q for q in ctx.captured_queries
            if "django_cache" not in q["sql"] and "SAVEPOINT" not in q["sql"]
        ]
        self.assertLessEqual(len(data_queries), 12, [q["sql"][:80] for q in data_queries])

    def test_product_detail(self):
        resp = self.client.get("/api/v1/products/brembo-p83-145-front-brake-pads/")
        self.assertEqual(resp.status_code, 200)
        body = resp.json()
        self.assertEqual(body["product"]["brand"], "Brembo")
        self.assertTrue(body["fits_summary"])
        self.assertEqual(body["structured_data"][0]["@type"], "Product")
        self.assertIn("isAccessoryOrSparePartFor", body["structured_data"][0])

    def test_search_part_number_redirects(self):
        # OEM number with separators stripped/differently formatted still hits.
        for q in ("04465-60280", "0446560280", "04465 60280"):
            resp = self.client.get("/api/v1/search/", {"q": q})
            self.assertEqual(resp.json().get("redirect_to"), "/products/brembo-p83-145-front-brake-pads/")

    def test_search_vehicle_intent_redirects(self):
        resp = self.client.get("/api/v1/search/", {"q": "prado 2018 brake pads"})
        data = resp.json()
        self.assertIn("redirect_to", data)
        self.assertTrue(data["redirect_to"].startswith("/car-parts/toyota/land-cruiser-prado/"))

    def test_search_text_fallback(self):
        resp = self.client.get("/api/v1/search/", {"q": "wiper"})
        results = resp.json()["results"]
        self.assertTrue(any("Wiper" in r["name"] for r in results))

    def test_seo_registry_thresholds(self):
        # A storefront with 0 products must be directive=410.
        empty = SeoPage.objects.filter(kind="vehicle", product_count=0).first()
        if empty:
            self.assertEqual(empty.directive, "410")
        # Product pages without images are noindex (seed has no images).
        p = SeoPage.objects.filter(kind="product").first()
        self.assertEqual(p.directive, "noindex")


class SitemapFeedTests(TestCase):
    @classmethod
    def setUpTestData(cls):
        call_command("seed_demo")
        call_command("build_variant_groups")
        call_command("rebuild_seo_registry")

    def test_build_sitemaps_writes_files(self):
        # Demo counts sit below the production thresholds; lower them so the
        # registry marks pages index and the sitemap has content to shard.
        from django.conf import settings
        from django.test import override_settings

        with override_settings(
            SEO_MIN_PRODUCTS_STOREFRONT=1, SEO_MIN_PRODUCTS_VEHICLE_CATEGORY=1
        ):
            call_command("rebuild_seo_registry")
            call_command("build_sitemaps")
        self.assertTrue((settings.SITEMAP_DIR / "sitemap.xml").exists())
        shard = (settings.SITEMAP_DIR / "sitemap-1.xml").read_text(encoding="utf-8")
        self.assertIn("<urlset", shard)
        self.assertIn("/car-parts/", shard)

    def test_merchant_feed_writes_xml(self):
        from django.conf import settings

        call_command("sync_merchant_feed", "--full")
        feed = (settings.FEED_DIR / "google-shopping.xml").read_text(encoding="utf-8")
        self.assertIn("<g:id>BRM-P83145</g:id>", feed)
        self.assertIn("g:custom_label_0", feed)

    def test_fitment_audit_clean(self):
        call_command("fitment_audit")  # raises SystemExit(1) on criticals
