from rest_framework import serializers

from ingestion.models import IngestionBatch, NormalizedEntry, RawRow
from review.serializers import ReviewStatusSerializer


class RawRowSerializer(serializers.ModelSerializer):
    class Meta:
        model = RawRow
        fields = ("id", "row_number", "raw_data", "parse_error", "created_at")


class IngestionBatchSerializer(serializers.ModelSerializer):
    class Meta:
        model = IngestionBatch
        fields = ("id", "source_type", "filename", "uploaded_at", "row_count", "error_count", "status")


class NormalizedEntrySerializer(serializers.ModelSerializer):
    review_status = ReviewStatusSerializer(read_only=True)

    class Meta:
        model = NormalizedEntry
        fields = (
            "id",
            "batch",
            "scope",
            "category",
            "activity_date",
            "description",
            "original_value",
            "original_unit",
            "normalized_value",
            "normalized_unit",
            "co2e_kg",
            "emission_factor",
            "emission_factor_source",
            "source_location",
            "is_edited",
            "edited_by",
            "edited_at",
            "created_at",
            "review_status",
        )
        read_only_fields = fields


class BatchDetailSerializer(serializers.ModelSerializer):
    entries = serializers.SerializerMethodField()
    error_rows = serializers.SerializerMethodField()

    class Meta:
        model = IngestionBatch
        fields = ("id", "source_type", "filename", "uploaded_at", "row_count", "error_count", "status", "entries", "error_rows")

    def get_entries(self, obj):
        entries = NormalizedEntry.objects.filter(batch=obj).select_related("review_status")
        return NormalizedEntrySerializer(entries, many=True).data

    def get_error_rows(self, obj):
        rows = RawRow.objects.filter(batch=obj).exclude(parse_error__isnull=True).exclude(parse_error="")
        return RawRowSerializer(rows, many=True).data
