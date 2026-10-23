# reviews/admin.py
from django.contrib import admin
from django.utils.html import format_html
from import_export.admin import ImportExportModelAdmin
from .models import Review


@admin.register(Review)
class ReviewAdmin(ImportExportModelAdmin):
    list_display = ['product', 'user', 'rating_stars', 'comment_preview', 'is_approved', 'created_at_formatted']
    list_filter = ['rating', 'is_approved', 'created_at']
    search_fields = ['product__name', 'user__username', 'comment']
    list_editable = ['is_approved']
    readonly_fields = ['created_at']
    list_per_page = 20

    fieldsets = (
        ("Thông tin đánh giá", {
            "fields": ("product", "user", "rating", "is_approved")
        }),
        ("Nội dung phản hồi", {
            "fields": ("comment",)
        }),
        ("Thời gian", {
            "fields": ("created_at",)
        }),
    )

    def rating_stars(self, obj):
        stars = '★' * obj.rating + '☆' * (5 - obj.rating)
        return format_html(
            '<span style="color:#f59e0b; font-size:1.05rem; letter-spacing:1px;">{}</span> <small class="text-muted">({}/5)</small>',
            stars, obj.rating
        )
    rating_stars.short_description = "Số sao"

    def comment_preview(self, obj):
        max_len = 60
        if len(obj.comment) > max_len:
            return f"{obj.comment[:max_len]}..."
        return obj.comment
    comment_preview.short_description = "Nội dung"

    def created_at_formatted(self, obj):
        return obj.created_at.strftime('%d/%m/%Y %H:%M')
    created_at_formatted.short_description = "Thời gian gửi"
