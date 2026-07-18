from django.contrib import admin
from treebeard.admin import TreeAdmin
from treebeard.forms import movenodeform_factory

from apps.catalog.models import (
    Brand,
    Category,
    ImportBatch,
    Offer,
    PartNumber,
    Product,
    ProductImage,
    StockMovement,
)
from apps.fitment.models import Fitment


@admin.register(Brand)
class BrandAdmin(admin.ModelAdmin):
    list_display = ["name", "is_oem"]
    prepopulated_fields = {"slug": ["name"]}
    search_fields = ["name"]


@admin.register(Category)
class CategoryAdmin(TreeAdmin):
    form = movenodeform_factory(Category)
    list_display = ["name", "slug", "kind", "google_category"]
    search_fields = ["name"]


class ProductImageInline(admin.TabularInline):
    model = ProductImage
    extra = 1


class OfferInline(admin.StackedInline):
    model = Offer
    extra = 0


class PartNumberInline(admin.TabularInline):
    model = PartNumber
    extra = 1
    readonly_fields = ["normalized"]


class FitmentInline(admin.TabularInline):
    model = Fitment
    extra = 1
    autocomplete_fields = ["generation", "trim", "engine"]


@admin.action(description="Copy fitment from another product (set SKU in the search box first)")
def copy_fitment_action(modeladmin, request, queryset):
    pass  # placeholder — real bulk-fitment tooling lands with the import UI


@admin.register(Product)
class ProductAdmin(admin.ModelAdmin):
    list_display = ["sku", "name", "brand", "category", "is_universal", "is_active"]
    list_filter = ["is_active", "is_universal", "condition", "brand"]
    search_fields = ["sku", "name", "mpn"]
    prepopulated_fields = {"slug": ["name"]}
    inlines = [OfferInline, ProductImageInline, PartNumberInline, FitmentInline]


@admin.register(Offer)
class OfferAdmin(admin.ModelAdmin):
    list_display = ["product", "price", "stock_qty", "availability", "updated_at"]
    list_filter = ["availability"]
    search_fields = ["product__sku", "product__name"]


@admin.register(StockMovement)
class StockMovementAdmin(admin.ModelAdmin):
    list_display = ["offer", "delta", "reason", "created_at"]


@admin.register(ImportBatch)
class ImportBatchAdmin(admin.ModelAdmin):
    list_display = ["id", "status", "created_at"]
    readonly_fields = ["report"]
