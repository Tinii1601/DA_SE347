from django.db import models
from django.utils.text import slugify
from unidecode import unidecode
from ckeditor_uploader.fields import RichTextUploadingField
import os

# 1. Định nghĩa Tên thuộc tính
class Attribute(models.Model):
    name = models.CharField(max_length=100, unique=True, verbose_name="Tên thuộc tính")
    
    class Meta:
        verbose_name = "Thuộc tính"
        verbose_name_plural = "Các thuộc tính"

    def __str__(self):
        return self.name

def product_cover_upload_to(instance, filename):
    ext = filename.split('.')[-1].lower()
    safe_title = slugify(unidecode(instance.name)) or "product"
    filename = f"{safe_title}.{ext}"
    return f"products/covers/{filename}"

# 2. Danh mục (Category)
class Category(models.Model):
    name = models.CharField(max_length=100, unique=True, verbose_name="Tên danh mục")
    slug = models.SlugField(max_length=100, unique=True, blank=True, verbose_name="Slug")
    description = models.TextField(blank=True, verbose_name="Mô tả")
    parent = models.ForeignKey('self', on_delete=models.CASCADE, null=True, blank=True, related_name='children', verbose_name="Danh mục cha")
    is_active = models.BooleanField(default=True, verbose_name="Kích hoạt")
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="Ngày tạo")
    
    attributes = models.ManyToManyField(Attribute, blank=True, verbose_name="Thuộc tính")

    class Meta:
        verbose_name = "Danh mục"
        verbose_name_plural = "Các thể loại"
        ordering = ['name']
        unique_together = ('slug', 'parent',)

    def __str__(self):
        full_path = [self.name]
        k = self.parent
        while k is not None:
            full_path.append(k.name)
            k = k.parent
        return ' -> '.join(full_path[::-1])

    def save(self, *args, **kwargs):
        if not self.slug:
            base = slugify(unidecode(self.name))
            slug = base
            i = 1
            while Category.objects.filter(slug=slug, parent=self.parent).exists():
                slug = f"{base}-{i}"
                i += 1
            self.slug = slug
        super().save(*args, **kwargs)

    def get_descendants_and_self_ids(self):
        result = [self.id]
        for child in self.children.all():
            result.extend(child.get_descendants_and_self_ids())
        return result

    def get_ancestors(self):
        ancestors = []
        k = self.parent
        while k is not None:
            ancestors.append(k)
            k = k.parent
        return ancestors[::-1]

    def get_all_attributes(self):
        """
        Lấy tất cả thuộc tính của danh mục hiện tại và các danh mục cha (kế thừa).
        """
        # 1. Lấy thuộc tính riêng của danh mục này
        all_attrs = list(self.attributes.all())

        # 2. Duyệt ngược lên các cha để lấy thêm thuộc tính
        parent = self.parent
        while parent:
            parent_attrs = parent.attributes.all()
            for attr in parent_attrs:
                # Chỉ thêm nếu chưa có (tránh trùng lặp)
                if attr not in all_attrs:
                    all_attrs.append(attr)
            parent = parent.parent
            
        return all_attrs

# 3. Sản phẩm (Product)
class Product(models.Model):
    category = models.ForeignKey(Category, on_delete=models.CASCADE, related_name='products', verbose_name="Danh mục")
    name = models.CharField(max_length=255, verbose_name="Tên sản phẩm")
    slug = models.SlugField(max_length=255, unique=True, blank=True, verbose_name="Slug")
    price = models.DecimalField(max_digits=10, decimal_places=2, verbose_name="Giá")
    discount_percentage = models.PositiveIntegerField(default=0, verbose_name="Phần trăm giảm giá")
    stock = models.PositiveIntegerField(default=0, verbose_name="Tồn kho")
    description = models.TextField(blank=True, verbose_name="Mô tả")
    cover_image = models.ImageField(upload_to=product_cover_upload_to, blank=True, null=True, verbose_name="Ảnh bìa")
    
    is_active = models.BooleanField(default=True, verbose_name="Kích hoạt")
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="Ngày tạo")
    updated_at = models.DateTimeField(auto_now=True, verbose_name="Cập nhật lần cuối")

    class Meta:
        verbose_name = "Sản phẩm"
        verbose_name_plural = "Danh sách sản phẩm"
        ordering = ['-created_at']

    def save(self, *args, **kwargs):
        if not self.slug:
            base = slugify(unidecode(self.name))
            slug = base
            i = 1
            while Product.objects.filter(slug=slug).exists():
                slug = f"{base}-{i}"
                i += 1
            self.slug = slug
        super().save(*args, **kwargs)

    def __str__(self):
        return self.name
        
    def get_final_price(self):
        if self.discount_percentage > 0:
            return self.price * (100 - self.discount_percentage) / 100
        return self.price

    @property
    def is_on_sale(self):
        return self.discount_percentage > 0

    def in_stock(self):
        return self.stock > 0

    def get_absolute_url(self):
        from django.urls import reverse
        # Assuming URL pattern will be updated to 'product_detail'
        return reverse('books:book_detail', args=[self.slug])

# 4. Giá trị của thuộc tính
class ProductAttributeValue(models.Model):
    product = models.ForeignKey(Product, on_delete=models.CASCADE, related_name='attribute_values', verbose_name="Sản phẩm")
    attribute = models.ForeignKey(Attribute, on_delete=models.CASCADE, verbose_name="Thuộc tính")
    value = models.TextField(verbose_name="Giá trị")

    class Meta:
        verbose_name = "Giá trị thuộc tính"
        verbose_name_plural = "Các giá trị thuộc tính"
        unique_together = ('product', 'attribute')

class ProductImage(models.Model):
    product = models.ForeignKey(Product, on_delete=models.CASCADE, related_name='images', verbose_name="Sản phẩm")
    image = models.ImageField(upload_to='products/gallery/', help_text="Ảnh album sản phẩm", verbose_name="Ảnh")
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="Ngày tạo")

    class Meta:
        verbose_name = "Ảnh sản phẩm"
        verbose_name_plural = "Album ảnh sản phẩm"

    def __str__(self):
        return f"Image for {self.product.name}"
