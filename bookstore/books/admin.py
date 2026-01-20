from django.contrib import admin
from import_export import resources, fields
from import_export.widgets import ForeignKeyWidget, ManyToManyWidget
from import_export.admin import ImportExportModelAdmin
from django.utils.safestring import mark_safe
from .models import Category, Product, Attribute, ProductAttributeValue, ProductImage

# --- Widgets ---

class CategoryParentForeignKeyWidget(ForeignKeyWidget):
    def clean(self, value, row=None, *args, **kwargs):
        val = super().clean(value, row=None, *args, **kwargs)
        if val:
            # val is the instance found by ForeignKeyWidget, or None/Exception
            # Actually super().clean returns the object or raises DoesNotExist
            return val
        
        # If value exists (string) but object not found (val is None implicitly usually raises)
        # We need to handle the lookup ourselves to support get_or_create
        if value:
            # Try to get or create the category by name
            obj, created = self.model.objects.get_or_create(name=value, defaults={'slug': ''})
            return obj
        return None

class AttributeM2MWidget(ManyToManyWidget):
    def clean(self, value, row=None, *args, **kwargs):
        if not value:
            return []
        # Case specific: Handle string "None" or similar garbage
        if str(value).lower().strip() in ['none', 'null', '']:
            return []
            
        names = [x.strip() for x in str(value).split(self.separator) if x.strip()]
        objects = []
        for name in names:
            # Case insensitive search or create? Keeping exact match for now but creating if missing
            obj, created = self.model.objects.get_or_create(name=name)
            objects.append(obj)
        return objects

# --- Resources ---

class AttributeResource(resources.ModelResource):
    name = fields.Field(attribute='name', column_name='name')

    class Meta:
        model = Attribute
        import_id_fields = ('name',)
        fields = ('id', 'name')
        skip_unchanged = True
        report_skipped = True

class CategoryResource(resources.ModelResource):
    parent = fields.Field(
        column_name='parent',
        attribute='parent',
        widget=CategoryParentForeignKeyWidget(Category, 'name')
    )
    attributes = fields.Field(
        column_name='attributes',
        attribute='attributes',
        widget=AttributeM2MWidget(Attribute, field='name', separator=';')
    )

    class Meta:
        model = Category
        import_id_fields = ('name',)
        fields = ('id', 'name', 'slug', 'description', 'parent', 'attributes')
        skip_unchanged = True
        report_skipped = True

    def before_import_row(self, row, **kwargs):
        if 'name' in row and ('slug' not in row or not row['slug']):
            from django.utils.text import slugify
            from unidecode import unidecode
            row['slug'] = slugify(unidecode(row['name']))
        
        # Set default description if empty
        if 'description' not in row or row['description'] is None:
            row['description'] = ''
    
    def after_save_instance(self, instance, row=None, **kwargs):
        # Implement inheritance logic: Add parent's attributes to child if not already present
        dry_run = kwargs.get('dry_run', False)
        if not dry_run and instance.parent:
            parent_attrs = instance.parent.attributes.all()
            for attr in parent_attrs:
                instance.attributes.add(attr)


class ProductResource(resources.ModelResource):
    category = fields.Field(
        column_name='category',
        attribute='category',
        widget=ForeignKeyWidget(Category, 'name')
    )

    class Meta:
        model = Product
        # Use name as identifier instead of slug if users don't provide slug
        import_id_fields = ('name',) 
        fields = ('id', 'category', 'name', 'slug', 'price', 'discount_percentage', 'stock', 'description', 'is_active')
        skip_unchanged = True
        report_skipped = True

    def before_import_row(self, row, **kwargs):
        # Auto-generate slug from name if missing
        if 'name' in row and ('slug' not in row or not row['slug']):
            from django.utils.text import slugify
            from unidecode import unidecode
            row['slug'] = slugify(unidecode(row['name']))

class ProductAttributeValueInline(admin.TabularInline):
    model = ProductAttributeValue
    extra = 1
    verbose_name = "Giá trị thuộc tính"
    verbose_name_plural = "Các giá trị thuộc tính"

class ProductImageInline(admin.TabularInline):
    model = ProductImage
    extra = 1
    verbose_name = "Ảnh album"
    verbose_name_plural = "Album ảnh"

# --- Admin Classes ---

@admin.register(Attribute)
class AttributeAdmin(ImportExportModelAdmin):
    resource_class = AttributeResource
    list_display = ['id', 'name']
    search_fields = ['name']
    ordering = ['name']

@admin.register(Category)
class CategoryAdmin(ImportExportModelAdmin):
    resource_class = CategoryResource
    list_display = ['name', 'slug', 'product_count', 'parent']
    search_fields = ['name', 'slug']
    prepopulated_fields = {'slug': ('name',)}
    list_filter = ['parent']
    
    def product_count(self, obj):
        return obj.products.count()
    product_count.short_description = "Số sản phẩm"

@admin.register(Product)
class ProductAdmin(ImportExportModelAdmin):
    resource_class = ProductResource
    list_display = ['name', 'category', 'price_formatted', 'is_active', 'stock', 'cover_image_thumb']
    list_filter = ['is_active', 'category', 'created_at']
    search_fields = ['name', 'description']
    prepopulated_fields = {'slug': ('name',)}
    list_editable = ['is_active', 'stock']
    readonly_fields = ['created_at', 'updated_at']
    inlines = [ProductAttributeValueInline, ProductImageInline]
    list_per_page = 20

    def cover_image_thumb(self, obj):
        if obj.cover_image:
            return mark_safe(
                f'<img src="{obj.cover_image.url}" width="40" height="60" style="object-fit: cover; border-radius: 4px;" />'
            )
        return "Không có ảnh"
    cover_image_thumb.short_description = "Ảnh bìa"

    def price_formatted(self, obj):
        return f"{obj.price:,.0f}₫"
    price_formatted.short_description = "Giá gốc"

    # Fieldset organization
    fieldsets = (
        ("Thông tin chung", {
            "fields": ("category", "name", "slug", "description", "is_active")
        }),
        ("Giá & Kho hàng", {
            "fields": ("price", "discount_percentage", "stock")
        }),
        ("Hình ảnh", {
            "fields": ("cover_image",)
        }),
        ("Thời gian", {
            "fields": ("created_at", "updated_at")
        }),
    )
