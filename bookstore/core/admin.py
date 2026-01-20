from django.contrib import admin
from import_export.admin import ImportExportModelAdmin
from .models import Store, ContentPage, NewsPost


@admin.register(Store)
class StoreAdmin(ImportExportModelAdmin):
    list_display = ("name", "city", "opening_hours", "is_active", "display_order")
    list_filter = ("is_active", "city")
    search_fields = ("name", "address", "city")
    ordering = ("display_order", "-created_at")


@admin.register(ContentPage)
class ContentPageAdmin(ImportExportModelAdmin):
    list_display = ("title", "slug", "is_active", "updated_at")
    list_filter = ("is_active",)
    search_fields = ("title", "slug")
    prepopulated_fields = {"slug": ("title",)}


@admin.register(NewsPost)
class NewsPostAdmin(ImportExportModelAdmin):
    list_display = ("id", "title", "category", "published_at", "is_active")
    list_filter = ("category", "is_active")
    search_fields = ("title", "summary", "slug")
    ordering = ("-created_at",)
