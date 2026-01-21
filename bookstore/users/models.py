# users/models.py
from django.db import models
from django.contrib.auth.models import User
from django.dispatch import receiver
from django.db.models.signals import post_save
import os
from PIL import Image
from django.core.exceptions import ValidationError
from django.utils import timezone
from datetime import date
from books.models import Product

# Tự động tạo thư mục nếu chưa có
def user_avatar_upload_to(instance, filename):
    ext = filename.split('.')[-1].lower()
    filename = f"{instance.user.username}.{ext}"
    return f"users/avatars/{filename}"
# Kiểm tra tuổi ≥ 14
def validate_min_age_14(value):
    today = date.today()
    age = today.year - value.year - (
        (today.month, today.day) < (value.month, value.day)
    )
    if age < 14:
        raise ValidationError("Người dùng phải đủ 14 tuổi trở lên.")

class UserProfile(models.Model):
    user = models.OneToOneField(
        User, on_delete=models.CASCADE, related_name='profile', verbose_name="Người dùng"
    )
    phone = models.CharField(max_length=15, blank=True, null=True, verbose_name="Số điện thoại")
    avatar = models.ImageField(upload_to=user_avatar_upload_to, blank=True, null=True, verbose_name="Ảnh đại diện")
    date_of_birth = models.DateField(blank=True,null=True, validators=[validate_min_age_14], verbose_name="Ngày sinh")
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="Ngày tạo")
    updated_at = models.DateTimeField(auto_now=True, verbose_name="Cập nhật lần cuối")

    class Meta:
        verbose_name = "Hồ sơ người dùng"
        verbose_name_plural = "Hồ sơ người dùng"

    def save(self, *args, **kwargs):
        self.full_clean() 
        super().save(*args, **kwargs)
        if self.avatar and os.path.exists(self.avatar.path):
            img = Image.open(self.avatar.path)
            img = img.convert("RGB")
            img.thumbnail((300, 300))
            img.save(self.avatar.path, quality=85)
    def __str__(self):
        return self.user.get_full_name() or self.user.username

class Address(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='addresses', verbose_name="Người dùng")
    full_name = models.CharField("Họ và tên", max_length=150)
    phone = models.CharField("Số điện thoại", max_length=15)
    address_line = models.CharField("Địa chỉ chi tiết (số nhà, đường...)", max_length=255)
    ward = models.CharField("Phường/Xã", max_length=100, blank=True)
    district = models.CharField("Quận/Huyện", max_length=100)
    city = models.CharField("Tỉnh/Thành phố", max_length=100)
    is_default = models.BooleanField("Mặc định", default=False)
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="Ngày tạo")

    class Meta:
        verbose_name = "Địa chỉ giao hàng"
        verbose_name_plural = "Danh sách địa chỉ"
        ordering = ['-is_default', '-created_at']

    def __str__(self):
        return f"{self.full_name} - {self.city}"

    # Khi lưu: nếu là mặc định → bỏ mặc định các cái khác
    def save(self, *args, **kwargs):
        if self.is_default:
            Address.objects.filter(user=self.user).update(is_default=False)
            self.is_default = True
        super().save(*args, **kwargs)

class WishlistItem(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='wishlist_items', verbose_name="Người dùng")
    product = models.ForeignKey(Product, on_delete=models.CASCADE, related_name='wishlisted_by', verbose_name="Sản phẩm")
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="Ngày thêm")

    class Meta:
        verbose_name = "Sản phẩm yêu thích"
        verbose_name_plural = "Danh sách yêu thích"
        unique_together = ('user', 'product')
        ordering = ['-created_at']

    def __str__(self):
        return f"{self.user.username} - {self.product.name}"
        
@receiver(post_save, sender=User)
def create_user_profile(sender, instance, created, **kwargs):
    if created:
        UserProfile.objects.create(user=instance)
