from django.contrib import admin

from plugins.sibar.models import SibarCheck


@admin.register(SibarCheck)
class SibarCheckAdmin(admin.ModelAdmin):
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
