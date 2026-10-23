# payment/admin.py
from django.contrib import admin
from django.utils.html import format_html
from import_export.admin import ImportExportModelAdmin

from .models import Payment


@admin.register(Payment)
class PaymentAdmin(ImportExportModelAdmin):
    list_display = (
        "order_link",
        "method_badge",
        "amount_formatted",
        "status_badge",
        "transaction_id_display",
        "paid_at_formatted",
        "created_at_formatted",
    )
    list_filter = ("method", "status", "created_at", "paid_at")
    search_fields = ("order__order_number", "transaction_id", "order__user__username")
    readonly_fields = ("created_at", "paid_at")
    list_per_page = 20

    fieldsets = (
        ("Thông tin giao dịch", {
            "fields": ("order", "method", "amount", "status", "transaction_id")
        }),
        ("Thời gian", {
            "fields": ("paid_at", "created_at")
        }),
    )

    def order_link(self, obj):
        try:
            order_num = obj.order.order_number
        except Exception:
            order_num = f"Đơn #{obj.order_id}"
        return format_html('<strong>{}</strong>', order_num)
    order_link.short_description = "Đơn hàng"

    def method_badge(self, obj):
        if obj.method == 'payos':
            return format_html(
                '<span class="badge" style="background:#e0f2fe;color:#0369a1;padding:5px 9px;border-radius:6px;font-weight:700;">'
                '<i class="fas fa-qrcode mr-1"></i>PayOS</span>'
            )
        return format_html(
            '<span class="badge" style="background:#f1f5f9;color:#334155;padding:5px 9px;border-radius:6px;font-weight:700;">'
            '<i class="fas fa-truck mr-1"></i>COD</span>'
        )
    method_badge.short_description = "Phương thức"

    def amount_formatted(self, obj):
        val = f"{obj.amount:,.0f}₫"
        return format_html('<strong style="color:#1a4d2e;">{}</strong>', val)
    amount_formatted.short_description = "Số tiền"

    def status_badge(self, obj):
        badges = {
            'pending': ('#fef3c7', '#92400e', 'fa-clock', 'Chờ thanh toán'),
            'completed': ('#dcfce7', '#15803d', 'fa-check-circle', 'Đã thanh toán'),
            'failed': ('#fee2e2', '#b91c1c', 'fa-exclamation-circle', 'Thất bại'),
            'canceled': ('#e2e8f0', '#475569', 'fa-ban', 'Đã hủy'),
        }
        bg, color, icon, label = badges.get(obj.status, ('#f1f5f9', '#475569', 'fa-circle', obj.get_status_display()))
        return format_html(
            '<span class="badge" style="background:{};color:{};padding:5px 9px;border-radius:6px;font-weight:700;">'
            '<i class="fas {} mr-1"></i>{}</span>',
            bg, color, icon, label
        )
    status_badge.short_description = "Trạng thái"

    def transaction_id_display(self, obj):
        if obj.transaction_id:
            return format_html('<code style="background:#f1f5f9;padding:2px 6px;border-radius:4px;">{}</code>', obj.transaction_id)
        return "—"
    transaction_id_display.short_description = "Mã GD"

    def paid_at_formatted(self, obj):
        return obj.paid_at.strftime('%d/%m/%Y %H:%M') if obj.paid_at else "—"
    paid_at_formatted.short_description = "Thời gian TT"

    def created_at_formatted(self, obj):
        return obj.created_at.strftime('%d/%m/%Y %H:%M')
    created_at_formatted.short_description = "Ngày tạo"
