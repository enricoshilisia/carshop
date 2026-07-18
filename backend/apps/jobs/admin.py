from django.contrib import admin

from apps.jobs.models import Job


@admin.register(Job)
class JobAdmin(admin.ModelAdmin):
    list_display = ["id", "name", "status", "priority", "attempts", "run_after", "finished_at"]
    list_filter = ["status", "name"]
    readonly_fields = ["error", "cursor", "attempts"]
