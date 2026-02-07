from django.contrib import admin

from .models import Collaborator, List, ListItem, TranslationCache


class CollaboratorInline(admin.TabularInline):
    model = Collaborator
    extra = 0


class ListItemInline(admin.TabularInline):
    model = ListItem
    extra = 0


@admin.register(List)
class ListAdmin(admin.ModelAdmin):
    list_display = ("title", "owner", "created_at", "updated_at")
    readonly_fields = ("share_token",)
    inlines = [CollaboratorInline, ListItemInline]


@admin.register(ListItem)
class ListItemAdmin(admin.ModelAdmin):
    list_display = ("text", "list", "source_language", "added_by", "is_checked")


@admin.register(TranslationCache)
class TranslationCacheAdmin(admin.ModelAdmin):
    list_display = ("item", "target_language", "translated_text")
