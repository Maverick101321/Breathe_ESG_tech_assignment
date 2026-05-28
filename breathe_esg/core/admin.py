from django.contrib import admin
from django.contrib.auth.admin import UserAdmin

from .models import Tenant, User


@admin.register(Tenant)
class TenantAdmin(admin.ModelAdmin):
    list_display = ("name", "slug", "is_active", "created_at")
    search_fields = ("name", "slug")


@admin.register(User)
class CustomUserAdmin(UserAdmin):
    model = User
    list_display = ("email", "username", "tenant", "role", "is_staff", "date_joined")
    list_filter = ("tenant", "role", "is_staff", "is_active")
    fieldsets = UserAdmin.fieldsets + (("Tenant", {"fields": ("tenant", "role")}),)
    add_fieldsets = UserAdmin.add_fieldsets + (
        ("Tenant", {"fields": ("tenant", "email", "role")}),
    )
    search_fields = ("email", "username")
