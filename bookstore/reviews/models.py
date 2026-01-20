from django.db import models
from books.models import Product
from django.contrib.auth.models import User

# Create your models here.
# reviews/models.py
class Review(models.Model):
    product = models.ForeignKey(Product, on_delete=models.CASCADE, related_name='reviews', verbose_name="Sản phẩm")
    user = models.ForeignKey(User, on_delete=models.CASCADE, verbose_name="Người dùng")
    rating = models.PositiveIntegerField(choices=[(i, i) for i in range(1, 6)], verbose_name="Đánh giá")
    comment = models.TextField(verbose_name="Bình luận")
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="Ngày tạo")
    is_approved = models.BooleanField(default=True, verbose_name="Đã duyệt")

    class Meta:
        verbose_name = "Đánh giá"
        verbose_name_plural = "Quản lý đánh giá"
        unique_together = ('product', 'user')
        ordering = ['-created_at']

    def __str__(self):
        return f"{self.user.username} - {self.product.name} ({self.rating} sao)"
