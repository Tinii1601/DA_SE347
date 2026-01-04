# users/models.py
from django.db import models
from django.contrib.auth.models import User
from django.dispatch import receiver
from django.db.models.signals import post_save
import os


# Tự động tạo thư mục nếu chưa có
def user_avatar_upload_to(instance, filename):
    ext = filename.split('.')[-1].lower()
    filename = f"{instance.user.username}.{ext}"
    return f"users/avatars/{filename}"


class UserProfile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='profile')
    phone = models.CharField("Số điện thoại", max_length=10, blank=True, null=True, unique=True)
    email = models.EmailField(
        "Email", 
        max_length=255, 
        blank=True, 
        null=True,  
        unique=True 
    )
    avatar = models.ImageField(
        "Ảnh đại diện",
        upload_to=user_avatar_upload_to,
        blank=True,
        null=True,
        help_text="Ảnh sẽ lưu tại: media/users/avatars/"
    )
    date_of_birth = models.DateField("Ngày sinh", blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = "Hồ sơ người dùng"
        verbose_name_plural = "Hồ sơ người dùng"

    def __str__(self):
        return f"{self.user.get_full_name() or self.user.username}"

    def avatar_url(self):
        if self.avatar and hasattr(self.avatar, 'url'):
            return self.avatar.url
        return "/static/img/default-avatar.jpg"  


class Address(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='addresses')
    full_name = models.CharField("Họ và tên", max_length=150)
    phone = models.CharField("Số điện thoại", max_length=15)
    address_line = models.CharField("Địa chỉ chi tiết (số nhà, đường...)", max_length=255)
    ward = models.CharField("Phường/Xã", max_length=100, blank=True)
    district = models.CharField("Quận/Huyện", max_length=100)
    city = models.CharField("Tỉnh/Thành phố", max_length=100)
    is_default = models.BooleanField("Mặc định", default=False)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = "Địa chỉ giao hàng"
        verbose_name_plural = "Địa chỉ giao hàng"
        ordering = ['-is_default', '-created_at']

    def __str__(self):
        return f"{self.full_name} - {self.city}"

    # Khi lưu: nếu là mặc định → bỏ mặc định các cái khác
    def save(self, *args, **kwargs):
        if self.is_default:
            Address.objects.filter(user=self.user).update(is_default=False)
            self.is_default = True
        super().save(*args, **kwargs)