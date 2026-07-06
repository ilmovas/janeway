from django.contrib import admin

from plugins.sabar.models import SabarCheck


@admin.register(SabarCheck)
class SabarCheckAdmin(admin.ModelAdmin):
    list_display = (
        "article",
        "status",
        "verdict",
        "confidence",
        "is_duplicate",
        "date_submitted",
        "date_completed",
    )
    list_filter = ("status", "verdict", "is_duplicate")
    search_fields = ("article__title", "report_id")
