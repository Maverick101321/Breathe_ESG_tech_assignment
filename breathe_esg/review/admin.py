from django.contrib import admin

from .models import AuditLog, ReviewStatus


@admin.register(ReviewStatus)
class ReviewStatusAdmin(admin.ModelAdmin):
    list_display = ("tenant", "entry", "status", "reviewed_by", "reviewed_at", "is_locked")
    list_filter = ("tenant", "status", "is_locked")


@admin.register(AuditLog)
class AuditLogAdmin(admin.ModelAdmin):
    list_display = ("tenant", "actor", "action", "target_type", "target_id", "timestamp")
    list_filter = ("tenant", "action", "target_type")
