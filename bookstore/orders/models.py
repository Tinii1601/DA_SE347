from django.db import models
from django.contrib.auth.models import User
from books.models import Product
from users.models import Address

# Create your models here.
# orders/models.py
class Coupon(models.Model):
    TYPE_CHOICES = [
        ('percent', 'Giảm phần trăm đơn hàng'),
        ('fixed', 'Giảm số tiền cố định'),
        ('ship_percent', 'Giảm phần trăm phí ship'),
        ('ship_fixed', 'Giảm tiền ship cố định'),
    ]
    
    code = models.CharField(max_length=50, unique=True, verbose_name="Mã giảm giá")
    discount_type = models.CharField(max_length=20, choices=TYPE_CHOICES, default='percent', verbose_name="Loại giảm giá")
    value = models.DecimalField(max_digits=10, decimal_places=2, default=0, help_text="Giá trị giảm (VNĐ hoặc %)", verbose_name="Giá trị")
    min_order_value = models.DecimalField(max_digits=10, decimal_places=2, default=0, verbose_name="Giá trị đơn hàng tối thiểu")
    max_discount = models.DecimalField(max_digits=10, decimal_places=2, default=0, help_text="Giảm tối đa (0 là không giới hạn)", verbose_name="Giảm tối đa")
    valid_from = models.DateTimeField(verbose_name="Có hiệu lực từ")
    valid_to = models.DateTimeField(verbose_name="Có hiệu lực đến")
    is_active = models.BooleanField(default=True, verbose_name="Kích hoạt")
    max_uses = models.PositiveIntegerField(default=100, verbose_name="Số lần sử dụng tối đa")
    used_count = models.PositiveIntegerField(default=0, verbose_name="Đã sử dụng")

    class Meta:
        verbose_name = "Mã giảm giá"
        verbose_name_plural = "Quản lý mã giảm giá"

    def __str__(self):
        return f"{self.code} - {self.get_discount_type_display()}"

    def is_valid(self):
        from django.utils import timezone
        now = timezone.now()
        return (self.is_active and self.valid_from <= now <= self.valid_to and self.used_count < self.max_uses)
    
    def calculate_discount(self, order_total, shipping_fee=0):
        discount = 0
        if order_total < self.min_order_value:
            return 0
            
        if self.discount_type == 'percent':
            discount = (order_total * self.value) / 100
            if self.max_discount > 0:
                discount = min(discount, self.max_discount)
        elif self.discount_type == 'fixed':
            discount = self.value
        elif self.discount_type == 'ship_percent':
            discount = (shipping_fee * self.value) / 100
            if self.max_discount > 0:
                discount = min(discount, self.max_discount)
        elif self.discount_type == 'ship_fixed':
            discount = min(self.value, shipping_fee)
            
        return discount
    
class Order(models.Model):
    STATUS_CHOICES = [
        ('pending', 'Chờ xác nhận'), ('confirmed', 'Đã xác nhận'),
        ('shipping', 'Đang giao'), ('delivered', 'Đã giao'), ('canceled', 'Đã hủy'),
    ]

    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='orders', verbose_name="Người dùng")
    order_number = models.CharField(max_length=20, unique=True, editable=False, verbose_name="Mã đơn hàng")
    shipping_address = models.ForeignKey(Address, on_delete=models.SET_NULL, null=True, verbose_name="Địa chỉ giao hàng")
    coupon = models.ForeignKey(Coupon, on_delete=models.SET_NULL, null=True, blank=True, verbose_name="Mã giảm giá")
    total_amount = models.DecimalField(max_digits=12, decimal_places=2, verbose_name="Tổng tiền")
    shipping_fee = models.DecimalField(max_digits=8, decimal_places=2, default=30000, verbose_name="Phí giao hàng")
    discount_amount = models.DecimalField(max_digits=10, decimal_places=2, default=0, verbose_name="Số tiền giảm")
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pending', verbose_name="Trạng thái")
    note = models.TextField(blank=True, verbose_name="Ghi chú")
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="Ngày tạo")
    updated_at = models.DateTimeField(auto_now=True, verbose_name="Cập nhật lần cuối")

    class Meta:
        verbose_name = "Đơn hàng"
        verbose_name_plural = "Danh sách đơn hàng"
        ordering = ['-created_at']
        indexes = [models.Index(fields=['order_number']), models.Index(fields=['status'])]

    def save(self, *args, **kwargs):
        if not self.order_number:
            from django.utils import timezone
            self.order_number = f"ORD{timezone.now().strftime('%Y%m%d%H%M%S')}"
        super().save(*args, **kwargs)

    def __str__(self):
        return f"Đơn hàng {self.order_number}"
    
class OrderItem(models.Model):
    order = models.ForeignKey(Order, on_delete=models.CASCADE, related_name='items', verbose_name="Đơn hàng")
    product = models.ForeignKey(Product, on_delete=models.CASCADE, verbose_name="Sản phẩm")
    price = models.DecimalField(max_digits=10, decimal_places=2, verbose_name="Giá")
    quantity = models.PositiveIntegerField(default=1, verbose_name="Số lượng")

    class Meta:
        verbose_name = "Chi tiết đơn hàng"
        verbose_name_plural = "Chi tiết đơn hàng"

    def get_subtotal(self):
        return self.price * self.quantity
