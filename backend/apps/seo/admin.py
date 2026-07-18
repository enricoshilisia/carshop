from django.contrib import admin

from apps.seo.models import SeoPage


@admin.register(SeoPage)
class SeoPageAdmin(admin.ModelAdmin):
    list_display = ["path", "kind", "directive", "product_count", "manual_override", "impressions_30d", "clicks_30d"]
    list_filter = ["kind", "directive", "manual_override"]
    search_fields = ["path", "title"]
    readonly_fields = ["last_computed"]
