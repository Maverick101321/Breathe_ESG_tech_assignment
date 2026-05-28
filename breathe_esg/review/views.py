from django.db.models import Sum
from django.utils import timezone
from rest_framework import status
from rest_framework.pagination import PageNumberPagination
from rest_framework.response import Response
from rest_framework.views import APIView

from core.permissions import get_tenant_object_or_403
from ingestion.models import IngestionBatch, NormalizedEntry
from ingestion.serializers import NormalizedEntrySerializer
from ingestion.services import serialize_for_json
from review.models import AuditLog, ReviewStatus
from review.serializers import AuditLogSerializer, ReviewStatusSerializer


class DashboardView(APIView):
    def get(self, request):
        statuses = ReviewStatus.objects.filter(tenant=request.user.tenant)
        approved_entries = NormalizedEntry.objects.filter(tenant=request.user.tenant, review_status__status="approved")
        return Response(
            {
                "total_pending": statuses.filter(status="pending").count(),
                "total_flagged": statuses.filter(status="flagged").count(),
                "total_approved": statuses.filter(status="approved").count(),
                "total_rejected": statuses.filter(status="rejected").count(),
                "total_co2e_approved": approved_entries.aggregate(total=Sum("co2e_kg"))["total"] or 0,
                "breakdown_by_scope": {
                    row["scope"]: row["total"]
                    for row in approved_entries.values("scope").annotate(total=Sum("co2e_kg"))
                },
            }
        )


class EntryListView(APIView):
    def get(self, request):
        entries = NormalizedEntry.objects.filter(tenant=request.user.tenant).select_related("review_status", "batch")
        if request.query_params.get("status"):
            entries = entries.filter(review_status__status=request.query_params["status"])
        if request.query_params.get("scope"):
            entries = entries.filter(scope=request.query_params["scope"])
        if request.query_params.get("source_type"):
            entries = entries.filter(batch__source_type=request.query_params["source_type"])
        if request.query_params.get("batch_id"):
            entries = entries.filter(batch_id=request.query_params["batch_id"])
        entries = entries.order_by("-created_at")
        paginator = PageNumberPagination()
        page = paginator.paginate_queryset(entries, request)
        return paginator.get_paginated_response(NormalizedEntrySerializer(page, many=True).data)


class EntryDetailView(APIView):
    editable_fields = {"co2e_kg", "activity_date", "description", "category"}

    def get(self, request, entry_id):
        entry = get_tenant_object_or_403(NormalizedEntry.objects.select_related("review_status"), request, id=entry_id)
        return Response(NormalizedEntrySerializer(entry).data)

    def patch(self, request, entry_id):
        entry = get_tenant_object_or_403(NormalizedEntry.objects.select_related("review_status"), request, id=entry_id)
        if entry.review_status.is_locked:
            return Response({"detail": "Entry is locked"}, status=status.HTTP_400_BAD_REQUEST)

        before_state = NormalizedEntrySerializer(entry).data
        for field in self.editable_fields:
            if field in request.data:
                setattr(entry, field, request.data[field])
        entry.is_edited = True
        entry.edited_by = request.user
        entry.edited_at = timezone.now()
        entry.save(update_fields=[*self.editable_fields, "is_edited", "edited_by", "edited_at"])
        after_state = NormalizedEntrySerializer(entry).data
        AuditLog.objects.create(
            tenant=request.user.tenant,
            actor=request.user,
            action="edited",
            target_type="NormalizedEntry",
            target_id=entry.id,
            before_state=serialize_for_json(before_state),
            after_state=serialize_for_json(after_state),
        )
        return Response(NormalizedEntrySerializer(entry).data)


class ReviewActionView(APIView):
    transitions = {
        "pending": {"approve", "flag", "reject"},
        "flagged": {"approve", "reject"},
        "approved": set(),
        "rejected": set(),
    }

    def post(self, request, entry_id):
        entry = get_tenant_object_or_403(NormalizedEntry.objects.select_related("review_status"), request, id=entry_id)
        review_status = entry.review_status
        action = request.data.get("action")
        reason = request.data.get("reason", "")
        if action not in {"approve", "flag", "reject"}:
            return Response({"detail": "Invalid action"}, status=status.HTTP_400_BAD_REQUEST)
        if action not in self.transitions.get(review_status.status, set()):
            return Response({"detail": "Invalid state transition"}, status=status.HTTP_400_BAD_REQUEST)

        before_state = ReviewStatusSerializer(review_status).data
        review_status.status = {"approve": "approved", "flag": "flagged", "reject": "rejected"}[action]
        review_status.reviewed_by = request.user
        review_status.reviewed_at = timezone.now()
        if action == "flag":
            review_status.flag_reason = reason
        if action == "reject":
            review_status.rejection_reason = reason
        if action == "approve":
            review_status.is_locked = True
        review_status.save()
        after_state = ReviewStatusSerializer(review_status).data

        AuditLog.objects.create(
            tenant=request.user.tenant,
            actor=request.user,
            action={"approve": "approved", "flag": "flagged", "reject": "rejected"}[action],
            target_type="ReviewStatus",
            target_id=review_status.id,
            before_state=serialize_for_json(before_state),
            after_state=serialize_for_json(after_state),
            notes=reason,
        )
        return Response(ReviewStatusSerializer(review_status).data)


class AuditLogView(APIView):
    def get(self, request):
        logs = AuditLog.objects.filter(tenant=request.user.tenant).order_by("-timestamp")
        if request.query_params.get("target_type"):
            logs = logs.filter(target_type=request.query_params["target_type"])
        if request.query_params.get("target_id"):
            logs = logs.filter(target_id=request.query_params["target_id"])
        return Response(AuditLogSerializer(logs, many=True).data)
