from django.contrib import admin

from .models import LanguagePair


@admin.register(LanguagePair)
class LanguagePairAdmin(admin.ModelAdmin):
    list_display = ("source_name", "source_code", "target_name", "target_code", "enabled")
    list_filter = ("enabled", "source_name")
    list_editable = ("enabled",)
    search_fields = ("source_name", "target_name", "source_code", "target_code")
    ordering = ("source_name", "target_name")
