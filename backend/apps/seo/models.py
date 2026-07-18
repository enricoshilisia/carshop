from django.db import models

from apps.catalog.models import Category, Product
from apps.vehicles.models import VariantGroup


class SeoPage(models.Model):
    """The SEO Page Registry. Not every URL deserves Google — this table decides."""

    KIND = [
        ("vehicle", "Vehicle storefront"),
        ("vehicle_category", "Vehicle + category"),
        ("category", "Category"),
        ("brand", "Brand"),
        ("product", "Product"),
    ]
    DIRECTIVE = [
        ("index", "index"),
        ("noindex", "noindex"),
        ("canonical", "canonical"),
        ("410", "410 Gone"),
    ]

    kind = models.CharField(max_length=24, choices=KIND, db_index=True)
    path = models.CharField(max_length=400, unique=True)
    variant_group = models.ForeignKey(VariantGroup, null=True, blank=True, on_delete=models.CASCADE)
    category = models.ForeignKey(Category, null=True, blank=True, on_delete=models.CASCADE)
    product = models.ForeignKey(Product, null=True, blank=True, on_delete=models.CASCADE)

    product_count = models.PositiveIntegerField(default=0, db_index=True)
    directive = models.CharField(max_length=12, default="noindex", db_index=True, choices=DIRECTIVE)
    canonical_to = models.CharField(max_length=400, blank=True)
    priority = models.FloatField(default=0.5)

    title = models.CharField(max_length=200, blank=True)
    meta_description = models.CharField(max_length=320, blank=True)
    h1 = models.CharField(max_length=200, blank=True)
    intro_html = models.TextField(blank=True)

    manual_override = models.BooleanField(default=False)  # admin wins over the rule engine
    impressions_30d = models.PositiveIntegerField(default=0)  # from GSC, Phase 8
    clicks_30d = models.PositiveIntegerField(default=0)
    last_computed = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.path} [{self.directive}]"
