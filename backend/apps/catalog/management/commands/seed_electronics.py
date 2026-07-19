"""Seed the general (non-fitment) catalog: laptops and mobile phones.

Same Product/Offer/feed machinery as car parts — Category.kind="general"
simply skips fitment. Idempotent; images added later via admin.
"""
from decimal import Decimal

from django.core.management.base import BaseCommand
from django.utils.text import slugify

from apps.catalog.models import Brand, Category, Offer, Product

BRANDS = ["Dell", "HP", "Lenovo", "Apple", "Samsung", "Tecno", "Infinix", "Xiaomi"]

# sku, brand, category-slug, name, mpn, price KES, specs
PRODUCTS = [
    ("DLL-LAT5440", "Dell", "laptops", "Dell Latitude 5440 14\" Core i5 16GB/512GB", "LAT5440",
     95000, {"cpu": "Intel Core i5-1345U", "ram_gb": 16, "storage_gb": 512, "screen_in": 14}),
    ("DLL-LAT7420", "Dell", "laptops", "Dell Latitude 7420 14\" Core i7 16GB/512GB", "LAT7420",
     78000, {"cpu": "Intel Core i7-1185G7", "ram_gb": 16, "storage_gb": 512, "screen_in": 14}),
    ("HP-EB840G8", "HP", "laptops", "HP EliteBook 840 G8 14\" Core i5 16GB/256GB", "EB840G8",
     72000, {"cpu": "Intel Core i5-1135G7", "ram_gb": 16, "storage_gb": 256, "screen_in": 14}),
    ("HP-PB450G9", "HP", "laptops", "HP ProBook 450 G9 15.6\" Core i5 8GB/512GB", "PB450G9",
     88000, {"cpu": "Intel Core i5-1235U", "ram_gb": 8, "storage_gb": 512, "screen_in": 15.6}),
    ("LNV-T14G3", "Lenovo", "laptops", "Lenovo ThinkPad T14 Gen 3 14\" Ryzen 7 16GB/512GB", "T14G3",
     98000, {"cpu": "AMD Ryzen 7 PRO 6850U", "ram_gb": 16, "storage_gb": 512, "screen_in": 14}),
    ("APL-MBA-M2", "Apple", "laptops", "Apple MacBook Air 13\" M2 8GB/256GB", "MBA-M2",
     145000, {"cpu": "Apple M2", "ram_gb": 8, "storage_gb": 256, "screen_in": 13.6}),
    ("SMS-A55", "Samsung", "phones", "Samsung Galaxy A55 5G 8GB/256GB", "SM-A556",
     52000, {"ram_gb": 8, "storage_gb": 256, "screen_in": 6.6, "network": "5G"}),
    ("SMS-S24", "Samsung", "phones", "Samsung Galaxy S24 8GB/256GB", "SM-S921",
     115000, {"ram_gb": 8, "storage_gb": 256, "screen_in": 6.2, "network": "5G"}),
    ("APL-IP15", "Apple", "phones", "Apple iPhone 15 128GB", "A3090",
     135000, {"storage_gb": 128, "screen_in": 6.1, "network": "5G"}),
    ("TEC-CAM30", "Tecno", "phones", "Tecno Camon 30 8GB/256GB", "CL6",
     32000, {"ram_gb": 8, "storage_gb": 256, "screen_in": 6.78, "network": "4G"}),
    ("TEC-SPARK20", "Tecno", "phones", "Tecno Spark 20 Pro 8GB/256GB", "KJ6",
     21000, {"ram_gb": 8, "storage_gb": 256, "screen_in": 6.78, "network": "4G"}),
    ("INF-NOTE40", "Infinix", "phones", "Infinix Note 40 Pro 8GB/256GB", "X6850",
     28500, {"ram_gb": 8, "storage_gb": 256, "screen_in": 6.78, "network": "4G"}),
    ("XIA-RN13", "Xiaomi", "phones", "Xiaomi Redmi Note 13 8GB/256GB", "23124RA7EO",
     26000, {"ram_gb": 8, "storage_gb": 256, "screen_in": 6.67, "network": "4G"}),
]


class Command(BaseCommand):
    help = "Seed laptops and mobile phones (general catalog, no fitment)."

    def handle(self, *args, **opts):
        brands = {}
        for name in BRANDS:
            brands[name], _ = Brand.objects.get_or_create(
                slug=slugify(name), defaults={"name": name}
            )

        cats = {}
        for slug in ("laptops", "phones"):
            cat = Category.objects.filter(slug=slug).first()
            if cat is None:
                cat = Category.add_root(name=slug.title(), slug=slug, kind="general")
            cats[slug] = cat

        created = 0
        for sku, brand, cat_slug, name, mpn, price, specs in PRODUCTS:
            product, was_new = Product.objects.get_or_create(
                sku=sku,
                defaults={
                    "brand": brands[brand],
                    "category": cats[cat_slug],
                    "name": name,
                    "slug": slugify(name)[:280],
                    "mpn": mpn,
                    "description": f"{name}. Genuine unit with warranty, delivered across Kenya.",
                    "specs": specs,
                    "condition": "new",
                },
            )
            created += was_new
            Offer.objects.get_or_create(
                product=product,
                defaults={"price": Decimal(price), "stock_qty": 10, "availability": "in_stock"},
            )

        self.stdout.write(self.style.SUCCESS(
            f"seed_electronics: {created} new products ({len(PRODUCTS)} total in data)"
        ))
