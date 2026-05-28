from django.shortcuts import get_object_or_404
from rest_framework.exceptions import PermissionDenied


def get_tenant_object_or_403(model_or_queryset, request, **lookup):
    obj = get_object_or_404(model_or_queryset, **lookup)
    if getattr(obj, "tenant_id", None) != request.user.tenant_id:
        raise PermissionDenied("Resource does not belong to the requesting tenant.")
    return obj


def require_same_tenant(obj, request):
    if getattr(obj, "tenant_id", None) != request.user.tenant_id:
        raise PermissionDenied("Resource does not belong to the requesting tenant.")
    return obj
