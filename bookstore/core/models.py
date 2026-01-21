from django.db import models
from ckeditor_uploader.fields import RichTextUploadingField
from django.utils.text import slugify
from django.urls import reverse
from urllib.parse import quote_plus


class Store(models.Model):
    name = models.CharField("Tên cửa hàng", max_length=150)
    address = models.CharField("Địa chỉ", max_length=255)
    city = models.CharField("Tỉnh/Thành phố", max_length=100, blank=True)
    map_url = models.URLField("Link bản đồ", blank=True)
    opening_hours = models.CharField("Giờ mở cửa", max_length=100, blank=True)
    description = models.TextField("Mô tả", blank=True)
    image = models.ImageField("Ảnh cửa hàng", upload_to="stores/", blank=True, null=True)
    is_active = models.BooleanField("Hiển thị", default=True)
    display_order = models.PositiveIntegerField("Thứ tự hiển thị", default=0)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["display_order", "-created_at"]
        verbose_name = "Cửa hàng"
        verbose_name_plural = "Hệ thống cửa hàng"

    def __str__(self):
        return self.name

    def get_map_link(self):
        if self.map_url:
            if self.map_url.startswith("http://") or self.map_url.startswith("https://"):
                return self.map_url
            query = self.map_url
        else:
            query = self.address
            if self.city:
                query = f"{query}, {self.city}"

        if not query:
            return ""

        return f"https://www.google.com/maps/search/?api=1&query={quote_plus(query)}"


class ContentPage(models.Model):
    title = models.CharField(max_length=200)
    slug = models.SlugField(max_length=200, unique=True)
    content_html = RichTextUploadingField()
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ["-updated_at"]
        verbose_name = "Trang nội dung"
        verbose_name_plural = "Trang nội dung"

    def __str__(self):
        return self.title


class NewsPost(models.Model):
    CATEGORY_PROMO = "promo"
    CATEGORY_EVENT = "event"
    CATEGORY_CHOICES = [
        (CATEGORY_PROMO, "Ưu đãi"),
        (CATEGORY_EVENT, "Sự kiện"),
    ]

    title = models.CharField(max_length=200)
    slug = models.SlugField(max_length=200, unique=True, blank=True)
    summary = models.CharField(max_length=300, blank=True)
    body_html = RichTextUploadingField()
    cover_image = models.ImageField(upload_to="news/", blank=True, null=True)
    category = models.CharField(max_length=20, choices=CATEGORY_CHOICES)
    published_at = models.DateField(blank=True, null=True)
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ["-created_at"]
        verbose_name = "Bài viết"
        verbose_name_plural = "Bài viết"

    def __str__(self):
        return self.title

    def get_absolute_url(self):
        return reverse("core:news_detail", args=[self.slug])

    def save(self, *args, **kwargs):
        if not self.slug:
            base_slug = slugify(self.title)
            slug = base_slug or "post"
            suffix = 1
            while NewsPost.objects.filter(slug=slug).exclude(pk=self.pk).exists():
                slug = f"{base_slug}-{suffix}"
                suffix += 1
            self.slug = slug
        super().save(*args, **kwargs)
