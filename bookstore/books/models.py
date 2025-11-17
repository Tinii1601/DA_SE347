# books/models.py
from django.db import models
from cloudinary.models import CloudinaryField
from django.contrib.auth.models import User


class Category(models.Model):
    name = models.CharField(max_length=100, unique=True)
    slug = models.SlugField(max_length=100, unique=True)
    description = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = "Thể loại"
        verbose_name_plural = "Các thể loại"
        ordering = ['name']
        indexes = [models.Index(fields=['slug'])]

    def __str__(self):
        return self.name
    
class Book(models.Model):
    title = models.CharField(max_length=255)
    slug = models.SlugField(max_length=255, unique=True)
    author = models.CharField(max_length=150)
    publisher = models.CharField(max_length=150, blank=True)
    isbn = models.CharField(max_length=13, unique=True, blank=True, null=True)
    description = models.TextField()
    price = models.DecimalField(max_digits=10, decimal_places=2)
    discount_price = models.DecimalField(max_digits=10, decimal_places=2, blank=True, null=True)
    stock = models.PositiveIntegerField(default=0)
    
    # CloudinaryField: tự động upload + tối ưu
    cover_image = CloudinaryField(
        'image',
        folder='books/covers',
        transformation=[
            {'width': 800, 'height': 1200, 'crop': 'fill', 'quality': 'auto', 'fetch_format': 'auto'}
        ],
        blank=True,
        null=True
    )

    category = models.ForeignKey(Category, on_delete=models.SET_NULL, null=True, related_name='books')
    published_year = models.PositiveIntegerField(blank=True, null=True)
    pages = models.PositiveIntegerField(blank=True, null=True)
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = "Sách"
        verbose_name_plural = "Danh sách sách"
        ordering = ['-created_at', 'title']
        indexes = [
            models.Index(fields=['title']),
            models.Index(fields=['author']),
            models.Index(fields=['price']),
            models.Index(fields=['slug']),
        ]
        unique_together = ('title', 'author')

    def __str__(self):
        return f"{self.title} - {self.author}"

    def get_final_price(self):
        return self.discount_price if self.discount_price else self.price

    def in_stock(self):
        return self.stock > 0