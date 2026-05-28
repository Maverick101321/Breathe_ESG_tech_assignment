from django.contrib import admin

from .models import IngestionBatch, NormalizedEntry, RawRow


@admin.register(IngestionBatch)
class IngestionBatchAdmin(admin.ModelAdmin):
    list_display = ("tenant", "source_type", "filename", "uploaded_by", "uploaded_at", "row_count", "error_count", "status")
    list_filter = ("tenant", "source_type", "status")


@admin.register(RawRow)
class RawRowAdmin(admin.ModelAdmin):
    list_display = ("tenant", "batch", "row_number", "parse_error", "created_at")
    list_filter = ("tenant", "batch")


@admin.register(NormalizedEntry)
class NormalizedEntryAdmin(admin.ModelAdmin):
    list_display = ("tenant", "batch", "scope", "category", "activity_date", "co2e_kg", "created_at")
    list_filter = ("tenant", "scope", "category")
