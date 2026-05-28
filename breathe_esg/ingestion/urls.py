from django.urls import path

from .views import BatchDetailView, BatchListView, UploadView


urlpatterns = [
    path("upload/", UploadView.as_view(), name="ingest-upload"),
    path("batches/", BatchListView.as_view(), name="ingest-batches"),
    path("batches/<uuid:batch_id>/", BatchDetailView.as_view(), name="ingest-batch-detail"),
]
