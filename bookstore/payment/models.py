from django.db import models
from orders.models import Order

class Payment(models.Model):
    METHOD_CHOICES = [
        ('cod', 'Thanh toán khi nhận hàng'), 
        ('vietqr', 'VietQR'),
    ]

    STATUS_CHOICES = [
        ('pending', 'Chờ thanh toán'), 
        ('completed', 'Đã thanh toán'),
        ('failed', 'Thất bại'), 
        ('canceled', 'Đã hủy'),
    ]

    order = models.OneToOneField(Order, on_delete=models.CASCADE, related_name='payment', verbose_name="Đơn hàng")
    method = models.CharField(max_length=20, choices=METHOD_CHOICES, verbose_name="Phương thức thanh toán")
    transaction_id = models.CharField(max_length=100, blank=True, verbose_name="Mã giao dịch")
    amount = models.DecimalField(max_digits=12, decimal_places=2, verbose_name="Số tiền")
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pending', verbose_name="Trạng thái")
    paid_at = models.DateTimeField(null=True, blank=True, verbose_name="Thời gian thanh toán")
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="Ngày tạo")

    class Meta:
        verbose_name = "Thanh toán"
        verbose_name_plural = "Lịch sử thanh toán"

    def __str__(self):
        return f"Thanh toán {self.order.order_number}"
