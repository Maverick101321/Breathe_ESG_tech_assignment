import uuid

from django.contrib.auth.models import AbstractUser
from django.db import models

from .middleware import get_current_tenant_id


class TenantScopedManager(models.Manager):
    def get_queryset(self):
        queryset = super().get_queryset()
        tenant_id = get_current_tenant_id()
        if tenant_id and any(field.name == "tenant" for field in self.model._meta.fields):
            return queryset.filter(tenant_id=tenant_id)
        return queryset


class Tenant(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    name = models.CharField(max_length=255)
    slug = models.SlugField(max_length=100, unique=True)
    created_at = models.DateTimeField(auto_now_add=True)
    is_active = models.BooleanField(default=True)

    def __str__(self):
        return self.name


class User(AbstractUser):
    ROLE_ANALYST = "analyst"
    ROLE_ADMIN = "admin"
    ROLE_CHOICES = [
        (ROLE_ANALYST, "Analyst"),
        (ROLE_ADMIN, "Admin"),
    ]

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    tenant = models.ForeignKey(Tenant, on_delete=models.CASCADE)
    email = models.EmailField(unique=True)
    role = models.CharField(max_length=20, choices=ROLE_CHOICES, default=ROLE_ANALYST)

    USERNAME_FIELD = "email"
    REQUIRED_FIELDS = ["username"]

    def __str__(self):
        return f"{self.email} ({self.tenant})"
