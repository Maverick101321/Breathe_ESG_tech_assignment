import uuid

from django.conf import settings
from django.db import models

from core.models import Tenant, TenantScopedManager


class IngestionBatch(models.Model):
    SOURCE_SAP = "sap_fuel_procurement"
    SOURCE_UTILITY = "utility_electricity"
    SOURCE_TRAVEL = "corporate_travel"
    SOURCE_TYPE_CHOICES = [
        (SOURCE_SAP, "SAP Fuel Procurement"),
        (SOURCE_UTILITY, "Utility Electricity"),
        (SOURCE_TRAVEL, "Corporate Travel"),
    ]

    STATUS_PROCESSING = "processing"
    STATUS_COMPLETE = "complete"
    STATUS_FAILED = "failed"
    STATUS_CHOICES = [
        (STATUS_PROCESSING, "Processing"),
        (STATUS_COMPLETE, "Complete"),
        (STATUS_FAILED, "Failed"),
    ]

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    tenant = models.ForeignKey(Tenant, on_delete=models.CASCADE)
    uploaded_by = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    source_type = models.CharField(max_length=50, choices=SOURCE_TYPE_CHOICES)
    filename = models.CharField(max_length=255)
    file_hash = models.CharField(max_length=64)
    uploaded_at = models.DateTimeField(auto_now_add=True)
    row_count = models.IntegerField(default=0)
    error_count = models.IntegerField(default=0)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default=STATUS_PROCESSING)

    objects = TenantScopedManager()
    all_objects = models.Manager()

    class Meta:
        unique_together = ("tenant", "file_hash")

    def __str__(self):
        return f"{self.filename} ({self.source_type})"


class RawRow(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    tenant = models.ForeignKey(Tenant, on_delete=models.CASCADE)
    batch = models.ForeignKey(IngestionBatch, related_name="rows", on_delete=models.CASCADE)
    row_number = models.IntegerField()
    raw_data = models.JSONField()
    parse_error = models.TextField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    objects = TenantScopedManager()
    all_objects = models.Manager()

    def __str__(self):
        return f"Row {self.row_number} in {self.batch.filename}"


class NormalizedEntry(models.Model):
    SCOPE_CHOICES = [
        ("scope_1", "Scope 1"),
        ("scope_2", "Scope 2"),
        ("scope_3", "Scope 3"),
    ]

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    tenant = models.ForeignKey(Tenant, on_delete=models.CASCADE)
    raw_row = models.OneToOneField(RawRow, on_delete=models.CASCADE)
    batch = models.ForeignKey(IngestionBatch, on_delete=models.CASCADE)
    scope = models.CharField(max_length=20, choices=SCOPE_CHOICES)
    category = models.CharField(max_length=100)
    activity_date = models.DateField()
    description = models.TextField()
    original_value = models.DecimalField(max_digits=18, decimal_places=6)
    original_unit = models.CharField(max_length=50)
    normalized_value = models.DecimalField(max_digits=18, decimal_places=6)
    normalized_unit = models.CharField(max_length=50)
    co2e_kg = models.DecimalField(max_digits=18, decimal_places=6)
    emission_factor = models.DecimalField(max_digits=18, decimal_places=8)
    emission_factor_source = models.CharField(max_length=255)
    source_location = models.CharField(max_length=255, blank=True)
    is_edited = models.BooleanField(default=False)
    edited_by = models.ForeignKey(settings.AUTH_USER_MODEL, null=True, blank=True, on_delete=models.SET_NULL)
    edited_at = models.DateTimeField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    objects = TenantScopedManager()
    all_objects = models.Manager()

    def __str__(self):
        return f"{self.category} - {self.co2e_kg} kg CO2e"
