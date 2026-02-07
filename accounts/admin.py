from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin

from .models import User


@admin.register(User)
class UserAdmin(BaseUserAdmin):
    list_display = ("email", "username", "preferred_language", "is_staff")
    fieldsets = BaseUserAdmin.fieldsets + (
        ("LingoList", {"fields": ("preferred_language",)}),
    )
    add_fieldsets = BaseUserAdmin.add_fieldsets + (
        ("LingoList", {"fields": ("preferred_language",)}),
    )
