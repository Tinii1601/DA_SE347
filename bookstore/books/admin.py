# books/admin.py
from django.contrib import admin
from import_export.admin import ImportExportModelAdmin
from django.utils.html import format_html
from .models import Category, Book


@admin.register(Category)
class CategoryAdmin(ImportExportModelAdmin):
    list_display = ['name', 'slug', 'book_count']
    search_fields = ['name']
    prepopulated_fields = {'slug': ('name',)}

    def book_count(self, obj):
        return obj.books.count()
    book_count.short_description = "Số sách"

@admin.register(Book)
class BookAdmin(ImportExportModelAdmin):
    list_display = ['title', 'author', 'final_price', 'stock', 'is_active', 'cover_image_thumb']
    list_filter = ['is_active', 'category', 'created_at']
    search_fields = ['title', 'author', 'isbn']
    readonly_fields = ['created_at', 'updated_at']
    list_editable = ['is_active']
    fieldsets = (
        (None, {
            "fields": (
                "title", "author", "publisher", "isbn",
                "category", "price", "discount_price", "stock", "is_active",
                "cover_image", "description", "detailed_description",
            )
        }),
        ("Thời gian", {"fields": ("created_at", "updated_at")}),
    )

    def cover_image_thumb(self, obj):
        if obj.cover_image:
            return format_html(
                '<img src="{}" width="60" height="90" style="object-fit: cover; border-radius: 4px;" />',
                obj.cover_image.url
            )
        return "Chưa có ảnh"
    cover_image_thumb.short_description = "Bìa sách"

    def final_price(self, obj):
        price = obj.get_final_price()
        return f"{price:,.0f}₫"
    final_price.short_description = "Giá bán"
