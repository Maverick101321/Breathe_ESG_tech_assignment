from rest_framework import serializers

from review.models import AuditLog, ReviewStatus


class ReviewStatusSerializer(serializers.ModelSerializer):
    class Meta:
        model = ReviewStatus
        fields = ("id", "status", "reviewed_by", "reviewed_at", "flag_reason", "rejection_reason", "is_locked")
        read_only_fields = fields


class AuditLogSerializer(serializers.ModelSerializer):
    class Meta:
        model = AuditLog
        fields = ("id", "actor", "action", "target_type", "target_id", "before_state", "after_state", "timestamp", "notes")
        read_only_fields = fields
