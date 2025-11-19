# books/models.py
from django.db import models
from django.utils.text import slugify
from unidecode import unidecode
import os


# Đường dẫn lưu ảnh: media/books/covers/nha-gia-kim.jpg
def book_cover_upload_to(instance, filename):
    """Tạo tên file an toàn + chống trùng"""
    ext = filename.split('.')[-1].lower()
    safe_title = slugify(unidecode(instance.title)) or "book"
    filename = f"{safe_title}.{ext}"
    return f"books/covers/{filename}"


class Category(models.Model):
    name = models.CharField(max_length=100, unique=True)
    slug = models.SlugField(max_length=100, unique=True, blank=True)
    description = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name_plural = "Các thể loại"
        ordering = ['name']

    def save(self, *args, **kwargs):
        if not self.slug:
            base = slugify(unidecode(self.name))
            slug = base
            i = 1
            while Category.objects.filter(slug=slug).exists():
                slug = f"{base}-{i}"
                i += 1
            self.slug = slug
        super().save(*args, **kwargs)

    def __str__(self):
        return self.name


class Book(models.Model):
    title = models.CharField(max_length=255)
    slug = models.SlugField(max_length=255, unique=True, blank=True)  # tự sinh
    author = models.CharField(max_length=150)
    publisher = models.CharField(max_length=150, blank=True)
    isbn = models.CharField(max_length=13, unique=True, blank=True, null=True)
    description = models.TextField()
    price = models.DecimalField(max_digits=10, decimal_places=2)
    discount_price = models.DecimalField(max_digits=10, decimal_places=2, blank=True, null=True)
    stock = models.PositiveIntegerField(default=0)

    cover_image = models.ImageField(
        upload_to=book_cover_upload_to,
        blank=True,
        null=True,
        help_text="Ảnh sẽ lưu tại: media/books/covers/"
    )

    category = models.ForeignKey(Category, on_delete=models.SET_NULL, null=True, related_name='books')
    published_year = models.PositiveIntegerField(blank=True, null=True)
    pages = models.PositiveIntegerField(blank=True, null=True)
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name_plural = "Danh sách sách"
        ordering = ['-created_at']
        unique_together = ('title', 'author')

    def __str__(self):
        return f"{self.title} - {self.author}"

    # TỰ ĐỘNG TẠO SLUG TỪ TITLE
    def save(self, *args, **kwargs):
        if not self.slug:
            base = slugify(unidecode(self.title))
            if not base:
                base = "book"
            slug = base
            i = 1
            while Book.objects.filter(slug=slug).exclude(pk=self.pk).exists():
                slug = f"{base}-{i}"
                i += 1
            self.slug = slug
        super().save(*args, **kwargs)

    def get_final_price(self):
        return self.discount_price if self.discount_price else self.price

    def in_stock(self):
        return self.stock > 0

    def get_average_rating(self):
        """Tính điểm đánh giá trung bình và số lượng đánh giá."""
        reviews = self.reviews.all()
        count = reviews.count()
        if count == 0:
            return {'average': 0, 'count': 0}
        
        total_rating = sum(review.rating for review in reviews)
        average = total_rating / count
        return {'average': round(average, 1), 'count': count}