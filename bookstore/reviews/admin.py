# reviews/admin.py
from django.contrib import admin
from import_export.admin import ImportExportModelAdmin
from .models import Review


@admin.register(Review)
class ReviewAdmin(ImportExportModelAdmin):
    list_display = ['product', 'user', 'rating', 'created_at', 'is_approved']
    list_filter = ['rating', 'is_approved', 'created_at']
    search_fields = ['product__name', 'user__username']
    list_editable = ['is_approved']
    readonly_fields = ['created_at']
