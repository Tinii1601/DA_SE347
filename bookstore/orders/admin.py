# orders/admin.py
from django.contrib import admin
from django.utils.html import format_html
from .models import Order, OrderItem, Coupon


@admin.register(Coupon)
class CouponAdmin(admin.ModelAdmin):
    list_display = ['code', 'discount_type', 'value', 'min_order_value', 'valid_to', 'is_active', 'used_count']
    list_filter = ['is_active', 'valid_from', 'valid_to', 'discount_type']
    search_fields = ['code']


class OrderItemInline(admin.TabularInline):
    model = OrderItem
    extra = 0
    readonly_fields = ['product', 'price', 'quantity']

@admin.register(Order)
class OrderAdmin(admin.ModelAdmin):
    list_display = ['order_number', 'user', 'total_amount_formatted', 'status', 'payment_method', 'created_at']
    list_filter = ['status', 'created_at', 'payment__method']
    search_fields = ['order_number', 'user__username']
    readonly_fields = ['order_number', 'created_at', 'updated_at']
    inlines = [OrderItemInline]

    def total_amount_formatted(self, obj):
        return f"{obj.total_amount:,.0f}₫"
    total_amount_formatted.short_description = "Tổng tiền"

    def payment_method(self, obj):
        if hasattr(obj, 'payment'):
            return obj.payment.get_method_display()
        return "Chưa thanh toán"
    payment_method.short_description = "Phương thức"