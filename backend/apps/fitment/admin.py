from django.contrib import admin

from apps.fitment.models import Fitment, FitmentIndex


@admin.register(Fitment)
class FitmentAdmin(admin.ModelAdmin):
    list_display = ["product", "generation", "trim", "engine", "year_from", "year_to", "position", "is_exclusion", "source"]
    list_filter = ["is_exclusion", "source", "generation__model__make"]
    search_fields = ["product__sku", "product__name"]
    autocomplete_fields = ["product", "generation", "trim", "engine"]


@admin.register(FitmentIndex)
class FitmentIndexAdmin(admin.ModelAdmin):
    list_display = ["product", "variant", "position"]
    search_fields = ["product__sku"]
    readonly_fields = ["product", "variant", "category", "brand", "position"]

    def has_add_permission(self, request):
        return False  # machine-written table
