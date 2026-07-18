from django.conf import settings
from django.db import models

from apps.catalog.models import Brand, Category, Product
from apps.vehicles.models import (
    OPEN_YEAR,
    VehicleEngine,
    VehicleGeneration,
    VehicleTrim,
    VehicleVariant,
)


class Fitment(models.Model):
    """
    One row = 'this product fits this vehicle line, these years, this position'.
    Authored at GENERATION level with optional trim/engine narrowing. NEVER per-year.
    """

    product = models.ForeignKey(Product, on_delete=models.CASCADE, related_name="fitments")
    generation = models.ForeignKey(VehicleGeneration, on_delete=models.CASCADE)
    trim = models.ForeignKey(VehicleTrim, null=True, blank=True, on_delete=models.CASCADE)
    engine = models.ForeignKey(VehicleEngine, null=True, blank=True, on_delete=models.CASCADE)
    drivetrain = models.CharField(max_length=8, blank=True)  # "" = any
    year_from = models.PositiveSmallIntegerField()
    year_to = models.PositiveSmallIntegerField(default=OPEN_YEAR)
    position = models.CharField(max_length=24, blank=True)  # front / rear / left / right
    notes = models.CharField(max_length=255, blank=True)
    # NEGATIVE rule: "fits J150 2015-2023 EXCEPT the 1KD engine".
    # Exclusions are subtracted after inclusion in resolve_variants().
    is_exclusion = models.BooleanField(default=False)
    source = models.CharField(max_length=32, default="manual")  # manual/supplier/tecdoc
    confidence = models.FloatField(default=1.0)
    verified_by = models.ForeignKey(
        settings.AUTH_USER_MODEL, null=True, blank=True, on_delete=models.SET_NULL
    )

    class Meta:
        indexes = [
            models.Index(fields=["generation", "year_from", "year_to"]),
            models.Index(fields=["product"]),
        ]

    def __str__(self):
        sign = "EXCLUDES" if self.is_exclusion else "fits"
        return f"{self.product} {sign} {self.generation} {self.year_from}-{self.year_to}"


class FitmentIndex(models.Model):
    """
    Flattened product ↔ variant edges. The ONLY table the storefront reads.
    Shared hosting cannot afford range math at request time — one index seek only.
    """

    product = models.ForeignKey(Product, on_delete=models.CASCADE)
    variant = models.ForeignKey(VehicleVariant, on_delete=models.CASCADE)
    category = models.ForeignKey(Category, on_delete=models.CASCADE)  # denorm for facet counts
    brand = models.ForeignKey(Brand, on_delete=models.CASCADE)  # denorm for facet counts
    position = models.CharField(max_length=24, blank=True)

    class Meta:
        unique_together = [("product", "variant", "position")]
        indexes = [
            models.Index(fields=["variant", "category"]),
            models.Index(fields=["variant", "brand"]),
        ]
        verbose_name_plural = "fitment index entries"

    def __str__(self):
        return f"{self.product_id} ↔ {self.variant_id}"
