from django.urls import path

from .views import AuditLogView, DashboardView, EntryDetailView, EntryListView, ReviewActionView


urlpatterns = [
    path("dashboard/", DashboardView.as_view(), name="review-dashboard"),
    path("entries/", EntryListView.as_view(), name="review-entries"),
    path("entries/<uuid:entry_id>/", EntryDetailView.as_view(), name="review-entry-detail"),
    path("entries/<uuid:entry_id>/action/", ReviewActionView.as_view(), name="review-entry-action"),
    path("audit/", AuditLogView.as_view(), name="review-audit"),
]
