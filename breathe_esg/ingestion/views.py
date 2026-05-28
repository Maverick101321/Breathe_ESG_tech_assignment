from rest_framework import status
from rest_framework.response import Response
from rest_framework.views import APIView

from core.permissions import get_tenant_object_or_403
from ingestion.models import IngestionBatch
from ingestion.serializers import BatchDetailSerializer, IngestionBatchSerializer
from ingestion.services import ingest_file


class UploadView(APIView):
    def post(self, request):
        upload = request.FILES.get("file")
        source_type = request.data.get("source_type")
        if not upload or not source_type:
            return Response({"detail": "file and source_type are required"}, status=status.HTTP_400_BAD_REQUEST)
        try:
            batch = ingest_file(
                tenant=request.user.tenant,
                user=request.user,
                file_obj=upload,
                source_type=source_type,
                filename=upload.name,
            )
        except ValueError as exc:
            return Response({"detail": str(exc)}, status=status.HTTP_400_BAD_REQUEST)
        return Response(
            {
                "batch_id": batch.id,
                "row_count": batch.row_count,
                "error_count": batch.error_count,
                "status": batch.status,
            },
            status=status.HTTP_201_CREATED,
        )


class BatchListView(APIView):
    def get(self, request):
        batches = IngestionBatch.objects.filter(tenant=request.user.tenant).order_by("-uploaded_at")
        return Response(IngestionBatchSerializer(batches, many=True).data)


class BatchDetailView(APIView):
    def get(self, request, batch_id):
        batch = get_tenant_object_or_403(IngestionBatch, request, id=batch_id)
        return Response(BatchDetailSerializer(batch).data)
