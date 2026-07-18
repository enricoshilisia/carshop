import re
from io import BytesIO
from pathlib import Path

from django.core.files.base import ContentFile
from django.db import models
from treebeard.mp_tree import MP_Node

AVAILABILITY = [
    ("in_stock", "In stock"),
    ("out_of_stock", "Out of stock"),
    ("preorder", "Pre-order"),
    ("backorder", "Backorder"),
]

CONDITION = [("new", "New"), ("used", "Used"), ("refurbished", "Refurbished")]

# Pillow derivative widths, generated once on upload — never at request time.
IMAGE_SIZES = (1200, 600, 300)


def normalize_part_number(raw: str) -> str:
    """Upper-case and strip separators so 04465-60280 == 0446560280 == 04465 60280."""
    return re.sub(r"[\s\-\./]", "", raw or "").upper()


class Brand(models.Model):
    name = models.CharField(max_length=120, unique=True)
    slug = models.SlugField(unique=True)
    logo = models.ImageField(upload_to="brands/", blank=True)
    is_oem = models.BooleanField(default=False)

    class Meta:
        ordering = ["name"]

    def __str__(self):
        return self.name


class Category(MP_Node):
    KIND = [("vehicle", "Vehicle part"), ("general", "General")]

    name = models.CharField(max_length=120)
    slug = models.SlugField(db_index=True)
    kind = models.CharField(max_length=12, choices=KIND, default="vehicle")
    google_category = models.CharField(max_length=255, blank=True)
    icon = models.CharField(max_length=64, blank=True)
    description = models.TextField(blank=True)
    seo_title = models.CharField(max_length=200, blank=True)
    seo_description = models.CharField(max_length=320, blank=True)

    node_order_by = ["name"]

    class Meta:
        verbose_name_plural = "categories"

    def __str__(self):
        return self.name


class Product(models.Model):
    sku = models.CharField(max_length=64, unique=True)
    mpn = models.CharField(max_length=64, blank=True, db_index=True)
    gtin = models.CharField(max_length=14, blank=True, db_index=True)
    brand = models.ForeignKey(Brand, on_delete=models.PROTECT, related_name="products")
    category = models.ForeignKey(Category, on_delete=models.PROTECT, related_name="products")
    name = models.CharField(max_length=255)
    slug = models.SlugField(max_length=280, unique=True)
    description = models.TextField(blank=True)
    specs = models.JSONField(default=dict, blank=True)
    condition = models.CharField(max_length=12, choices=CONDITION, default="new")
    weight_kg = models.DecimalField(max_digits=7, decimal_places=3, default=0)
    is_universal = models.BooleanField(default=False)
    is_active = models.BooleanField(default=True, db_index=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.name


class ProductImage(models.Model):
    product = models.ForeignKey(Product, on_delete=models.CASCADE, related_name="images")
    image = models.ImageField(upload_to="products/")
    alt = models.CharField(max_length=200, blank=True)
    sort_order = models.PositiveSmallIntegerField(default=0)
    is_primary = models.BooleanField(default=False)

    class Meta:
        ordering = ["-is_primary", "sort_order"]

    def __str__(self):
        return f"{self.product} image {self.pk}"

    def save(self, *args, **kwargs):
        super().save(*args, **kwargs)
        self._generate_derivatives()

    def _generate_derivatives(self):
        """1200/600/300 WebP written next to the original, once, on upload."""
        try:
            from PIL import Image
        except ImportError:  # pragma: no cover
            return
        if not self.image:
            return
        try:
            storage = self.image.storage
            src = Path(self.image.name)
            with self.image.open("rb") as fh:
                img = Image.open(fh)
                img.load()
            if img.mode not in ("RGB", "RGBA"):
                img = img.convert("RGB")
            for width in IMAGE_SIZES:
                dest = str(src.with_name(f"{src.stem}_{width}.webp"))
                if storage.exists(dest):
                    continue
                copy = img.copy()
                copy.thumbnail((width, width * 10))
                buf = BytesIO()
                copy.save(buf, "WEBP", quality=82)
                storage.save(dest, ContentFile(buf.getvalue()))
        except Exception:  # never let a thumbnail failure break a save
            pass


class Offer(models.Model):
    """Price + stock, separate from Product, so multi-seller is a later flag not a rewrite."""

    product = models.OneToOneField(Product, on_delete=models.CASCADE, related_name="offer")
    price = models.DecimalField(max_digits=12, decimal_places=2)  # KES
    compare_at = models.DecimalField(max_digits=12, decimal_places=2, null=True, blank=True)
    currency = models.CharField(max_length=3, default="KES")
    stock_qty = models.IntegerField(default=0)
    availability = models.CharField(max_length=16, choices=AVAILABILITY, db_index=True, default="in_stock")
    lead_time_days = models.PositiveSmallIntegerField(default=0)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.product} — {self.currency} {self.price}"


class StockMovement(models.Model):
    offer = models.ForeignKey(Offer, on_delete=models.CASCADE, related_name="movements")
    delta = models.IntegerField()
    reason = models.CharField(max_length=64, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.offer_id}: {self.delta:+d} ({self.reason})"


class PartNumber(models.Model):
    KIND = [
        ("oem", "OEM"),
        ("mpn", "MPN"),
        ("cross", "Cross-reference"),
        ("supersede", "Supersedes"),
    ]

    product = models.ForeignKey(Product, on_delete=models.CASCADE, related_name="part_numbers")
    number = models.CharField(max_length=64)
    normalized = models.CharField(max_length=64, db_index=True)
    kind = models.CharField(max_length=12, choices=KIND, default="mpn")
    # An OEM number belongs to Toyota, not to Brembo — hence its own brand FK.
    brand = models.ForeignKey(Brand, null=True, blank=True, on_delete=models.SET_NULL)

    def save(self, *args, **kwargs):
        self.normalized = normalize_part_number(self.number)
        super().save(*args, **kwargs)

    def __str__(self):
        return self.number


class ProductSearchDoc(models.Model):
    """One text blob per product for FULLTEXT (MySQL) / icontains fallback."""

    product = models.OneToOneField(Product, on_delete=models.CASCADE, related_name="search_doc")
    text = models.TextField()

    def __str__(self):
        return f"searchdoc:{self.product_id}"


class ImportBatch(models.Model):
    """XLSX bulk import staging. Dry-run by default; committed as a chunked Job."""

    STATUS = [
        ("uploaded", "Uploaded"),
        ("validated", "Validated"),
        ("committing", "Committing"),
        ("done", "Done"),
        ("failed", "Failed"),
    ]

    file = models.FileField(upload_to="imports/")
    status = models.CharField(max_length=12, choices=STATUS, default="uploaded")
    report = models.JSONField(default=dict, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name_plural = "import batches"

    def __str__(self):
        return f"Import #{self.pk} ({self.status})"
