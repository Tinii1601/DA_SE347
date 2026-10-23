# orders/admin.py
from django.contrib import admin
from django.utils.html import format_html
from django.utils import timezone
from import_export.admin import ImportExportModelAdmin
from .models import Order, OrderItem, Coupon


@admin.register(Coupon)
class CouponAdmin(ImportExportModelAdmin):
    list_display = ['code', 'discount_badge', 'min_order_formatted', 'usage_badge', 'valid_to', 'status_badge']
    list_filter = ['is_active', 'discount_type', 'valid_from', 'valid_to']
    search_fields = ['code']

    def discount_badge(self, obj):
        if 'percent' in obj.discount_type:
            val = f"{obj.value:.0f}%"
        else:
            val = f"{obj.value:,.0f}₫"
        return format_html(
            '<span class="badge" style="background:#e0f2fe;color:#0369a1;padding:4px 8px;font-weight:700;">'
            '{} ({})</span>',
            val, obj.get_discount_type_display()
        )
    discount_badge.short_description = "Giá trị giảm"

    def min_order_formatted(self, obj):
        return f"{obj.min_order_value:,.0f}₫"
    min_order_formatted.short_description = "Đơn tối thiểu"

    def usage_badge(self, obj):
        return format_html(
            '<span style="font-weight:600;">{}/{}</span>',
            obj.used_count, obj.max_uses
        )
    usage_badge.short_description = "Lượt dùng"

    def status_badge(self, obj):
        now = timezone.now()
        if not obj.is_active:
            return format_html('<span class="badge" style="background:#fee2e2;color:#b91c1c;">Vô hiệu</span>')
        if obj.valid_to < now:
            return format_html('<span class="badge" style="background:#fef3c7;color:#92400e;">Hết hạn</span>')
        if obj.used_count >= obj.max_uses:
            return format_html('<span class="badge" style="background:#e2e8f0;color:#475569;">Hết lượt</span>')
        return format_html('<span class="badge" style="background:#dcfce7;color:#15803d;">Khả dụng</span>')
    status_badge.short_description = "Trạng thái"


class OrderItemInline(admin.TabularInline):
    model = OrderItem
    extra = 0
    readonly_fields = ['product', 'price_formatted', 'quantity', 'subtotal_formatted']
    fields = ['product', 'price_formatted', 'quantity', 'subtotal_formatted']

    def price_formatted(self, obj):
        return f"{obj.price:,.0f}₫"
    price_formatted.short_description = "Đơn giá"

    def subtotal_formatted(self, obj):
        return f"{obj.get_subtotal():,.0f}₫"
    subtotal_formatted.short_description = "Thành tiền"


@admin.register(OrderItem)
class OrderItemAdmin(ImportExportModelAdmin):
    list_display = ("order", "product", "price_formatted", "quantity", "subtotal_formatted")
    search_fields = ("order__order_number", "product__name")
    list_filter = ("order__status",)

    def price_formatted(self, obj):
        return f"{obj.price:,.0f}₫"
    price_formatted.short_description = "Đơn giá"

    def subtotal_formatted(self, obj):
        return f"{obj.get_subtotal():,.0f}₫"
    subtotal_formatted.short_description = "Thành tiền"


@admin.register(Order)
class OrderAdmin(ImportExportModelAdmin):
    list_display = [
        'order_number',
        'customer_info',
        'total_amount_formatted',
        'status_badge',
        'payment_badge',
        'created_at_formatted',
    ]
    list_filter = ['status', 'created_at', 'payment__method', 'payment__status']
    search_fields = [
        'order_number',
        'user__username',
        'user__email',
        'shipping_address__full_name',
        'shipping_address__phone',
    ]
    readonly_fields = ['order_number', 'created_at', 'updated_at', 'total_amount_display']
    inlines = [OrderItemInline]
    list_per_page = 20

    fieldsets = (
        ("Thông tin đơn hàng", {
            "fields": ("order_number", "user", "status", "created_at", "updated_at")
        }),
        ("Giao hàng & Người nhận", {
            "fields": ("shipping_address", "note")
        }),
        ("Chi phí & Khuyến mãi", {
            "fields": ("total_amount", "shipping_fee", "discount_amount", "coupon")
        }),
    )

    def customer_info(self, obj):
        name = obj.shipping_address.full_name if obj.shipping_address else (obj.user.get_full_name() or obj.user.username)
        phone = obj.shipping_address.phone if obj.shipping_address else ""
        if phone:
            return format_html('<strong>{}</strong><br><small class="text-muted">{}</small>', name, phone)
        return format_html('<strong>{}</strong>', name)
    customer_info.short_description = "Khách hàng"

    def total_amount_formatted(self, obj):
        return format_html('<strong style="color:#1a4d2e; font-size: 0.95rem;">{:,.0f}₫</strong>', obj.total_amount)
    total_amount_formatted.short_description = "Tổng tiền"

    def total_amount_display(self, obj):
        return f"{obj.total_amount:,.0f}₫"
    total_amount_display.short_description = "Tổng tiền"

    def status_badge(self, obj):
        badges = {
            'pending': ('#fef3c7', '#92400e', 'fa-clock', 'Chờ xác nhận'),
            'confirmed': ('#e0f2fe', '#0369a1', 'fa-check', 'Đã xác nhận'),
            'shipping': ('#ede9fe', '#6d28d9', 'fa-shipping-fast', 'Đang giao'),
            'delivered': ('#dcfce7', '#15803d', 'fa-check-circle', 'Đã giao'),
            'canceled': ('#fee2e2', '#b91c1c', 'fa-times-circle', 'Đã hủy'),
        }
        bg, color, icon, label = badges.get(obj.status, ('#f1f5f9', '#475569', 'fa-circle', obj.get_status_display()))
        return format_html(
            '<span class="badge" style="background:{};color:{};padding:5px 9px;border-radius:6px;font-weight:700;">'
            '<i class="fas {} mr-1"></i>{}</span>',
            bg, color, icon, label
        )
    status_badge.short_description = "Trạng thái"

    def payment_badge(self, obj):
        if hasattr(obj, 'payment') and obj.payment:
            method = obj.payment.method
            status = obj.payment.status
            if method == 'payos':
                if status == 'completed':
                    return format_html(
                        '<span class="badge" style="background:#dcfce7;color:#15803d;padding:5px 9px;border-radius:6px;font-weight:700;">'
                        '<i class="fas fa-qrcode mr-1"></i>PayOS (Đã TT)</span>'
                    )
                return format_html(
                    '<span class="badge" style="background:#e0f2fe;color:#0369a1;padding:5px 9px;border-radius:6px;font-weight:700;">'
                    '<i class="fas fa-qrcode mr-1"></i>PayOS (Chờ)</span>'
                )
            else:
                return format_html(
                    '<span class="badge" style="background:#f1f5f9;color:#334155;padding:5px 9px;border-radius:6px;font-weight:700;">'
                    '<i class="fas fa-truck mr-1"></i>COD</span>'
                )
        return format_html('<span class="badge" style="background:#f8fafc;color:#94a3b8;padding:5px 9px;border-radius:6px;">Chưa TT</span>')
    payment_badge.short_description = "Thanh toán"

    def created_at_formatted(self, obj):
        return obj.created_at.strftime('%d/%m/%Y %H:%M')
    created_at_formatted.short_description = "Ngày đặt"
