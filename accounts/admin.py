from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin

from .models import PatientProfile, User


class PatientProfileInline(admin.StackedInline):
    model = PatientProfile
    can_delete = False
    extra = 0


@admin.register(User)
class UserAdmin(BaseUserAdmin):
    list_display = ("username", "email", "display_name", "role", "phone", "is_active")
    list_filter = ("role", "is_active", "is_staff")
    search_fields = ("username", "email", "first_name", "last_name", "phone")
    fieldsets = BaseUserAdmin.fieldsets + (
        ("Practice", {"fields": ("role", "phone", "whatsapp")}),
    )
    add_fieldsets = BaseUserAdmin.add_fieldsets + (
        ("Practice", {"fields": ("role", "phone", "whatsapp")}),
    )
    inlines = [PatientProfileInline]


@admin.register(PatientProfile)
class PatientProfileAdmin(admin.ModelAdmin):
    list_display = ("user", "primary_concern", "created_at")
    search_fields = ("user__username", "user__email", "primary_concern")
    raw_id_fields = ("user",)
