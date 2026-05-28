import uuid

from django.conf import settings
from django.db import models

from core.models import Tenant, TenantScopedManager
from ingestion.models import NormalizedEntry


class ReviewStatus(models.Model):
    STATUS_CHOICES = [
        ("pending", "Pending"),
        ("flagged", "Flagged"),
        ("approved", "Approved"),
        ("rejected", "Rejected"),
    ]

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    tenant = models.ForeignKey(Tenant, on_delete=models.CASCADE)
    entry = models.OneToOneField(NormalizedEntry, related_name="review_status", on_delete=models.CASCADE)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default="pending")
    reviewed_by = models.ForeignKey(settings.AUTH_USER_MODEL, null=True, blank=True, on_delete=models.SET_NULL)
    reviewed_at = models.DateTimeField(null=True, blank=True)
    flag_reason = models.TextField(blank=True)
    rejection_reason = models.TextField(blank=True)
    is_locked = models.BooleanField(default=False)

    objects = TenantScopedManager()
    all_objects = models.Manager()

    def __str__(self):
        return f"{self.entry_id}: {self.status}"


class AuditLog(models.Model):
    ACTION_CHOICES = [
        ("uploaded", "Uploaded"),
        ("parsed", "Parsed"),
        ("edited", "Edited"),
        ("flagged", "Flagged"),
        ("approved", "Approved"),
        ("rejected", "Rejected"),
        ("locked", "Locked"),
    ]

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    tenant = models.ForeignKey(Tenant, on_delete=models.CASCADE)
    actor = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    action = models.CharField(max_length=20, choices=ACTION_CHOICES)
    target_type = models.CharField(max_length=50)
    target_id = models.UUIDField()
    before_state = models.JSONField(null=True)
    after_state = models.JSONField(null=True)
    timestamp = models.DateTimeField(auto_now_add=True)
    notes = models.TextField(blank=True)

    objects = TenantScopedManager()
    all_objects = models.Manager()

    def __str__(self):
        return f"{self.action} {self.target_type}:{self.target_id}"
