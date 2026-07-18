from django.contrib import admin

from apps.vehicles.models import (
    VehicleEngine,
    VehicleGeneration,
    VehicleMake,
    VehicleModel,
    VehicleModelAlias,
    VehicleRegistrationLookup,
    VehicleTrim,
    VehicleVariant,
    VariantGroup,
)


class VehicleModelAliasInline(admin.TabularInline):
    model = VehicleModelAlias
    extra = 1


@admin.register(VehicleMake)
class VehicleMakeAdmin(admin.ModelAdmin):
    list_display = ["name", "slug", "popularity", "is_active"]
    prepopulated_fields = {"slug": ["name"]}


@admin.register(VehicleModel)
class VehicleModelAdmin(admin.ModelAdmin):
    list_display = ["name", "make", "slug"]
    list_filter = ["make"]
    prepopulated_fields = {"slug": ["name"]}
    inlines = [VehicleModelAliasInline]


class VehicleTrimInline(admin.TabularInline):
    model = VehicleTrim
    extra = 1


class VehicleEngineInline(admin.TabularInline):
    model = VehicleEngine
    extra = 1


@admin.register(VehicleGeneration)
class VehicleGenerationAdmin(admin.ModelAdmin):
    list_display = ["__str__", "code", "year_from", "year_to", "body_type"]
    list_filter = ["model__make"]
    search_fields = ["code", "model__name", "model__make__name"]
    prepopulated_fields = {"slug": ["code"]}
    inlines = [VehicleTrimInline, VehicleEngineInline]


@admin.register(VehicleVariant)
class VehicleVariantAdmin(admin.ModelAdmin):
    list_display = ["display_name", "market", "is_active"]
    list_filter = ["market", "is_active", "generation__model__make"]
    autocomplete_fields = ["generation", "trim", "engine"]
    search_fields = ["generation__code", "generation__model__name"]


@admin.register(VariantGroup)
class VariantGroupAdmin(admin.ModelAdmin):
    list_display = ["canonical_path", "product_count", "fingerprint"]
    readonly_fields = ["fingerprint", "canonical_path", "product_count"]
    search_fields = ["canonical_path"]


@admin.register(VehicleRegistrationLookup)
class VehicleRegistrationLookupAdmin(admin.ModelAdmin):
    list_display = ["plate", "variant", "confidence", "resolved_at"]
    search_fields = ["plate", "vin"]


# Needed for autocomplete_fields above.
@admin.register(VehicleTrim)
class VehicleTrimAdmin(admin.ModelAdmin):
    search_fields = ["name", "generation__code"]


@admin.register(VehicleEngine)
class VehicleEngineAdmin(admin.ModelAdmin):
    search_fields = ["display", "code", "generation__code"]
