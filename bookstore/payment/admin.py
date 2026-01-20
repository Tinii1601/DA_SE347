from django.contrib import admin
from import_export.admin import ImportExportModelAdmin

from .models import Payment


@admin.register(Payment)
class PaymentAdmin(ImportExportModelAdmin):
    list_display = ("order", "method", "amount", "status", "paid_at", "created_at")
    list_filter = ("method", "status", "paid_at", "created_at")
    search_fields = ("order__order_number", "transaction_id")
