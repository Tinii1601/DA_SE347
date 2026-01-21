from django.contrib import admin
from import_export import resources, fields
from import_export.widgets import ForeignKeyWidget, ManyToManyWidget
from import_export.admin import ImportExportModelAdmin
from django.utils.safestring import mark_safe
from .models import Category, Product, Attribute, ProductAttributeValue, ProductImage


class CategoryParentForeignKeyWidget(ForeignKeyWidget):
    def clean(self, value, row=None, *args, **kwargs):
        if not value:
            return None
            
        try:
            # Try to get existing object using standard widget logic
            return super().clean(value, row=None, *args, **kwargs)
        except Exception:
            # If failed (DoesNotExist or others), create it
            # Remove any trailing spaces from lookup value
            clean_val = str(value).strip()
            print(f"Creating parent category: {clean_val}")
            obj, created = self.model.objects.get_or_create(name=clean_val, defaults={'slug': ''})
            return obj

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
        column_name='parent ',  # Note the space in header "parent "
        attribute='parent',
        widget=CategoryParentForeignKeyWidget(Category, 'name')
    )

    class Meta:
        model = Category
        import_id_fields = ('name',)
        fields = ('id', 'name', 'slug', 'description', 'parent')
        # Disable skipping to force updates for existing categories (like attributes)
        skip_unchanged = False
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
        dry_run = kwargs.get('dry_run', False)
        if dry_run:
            return

        # 1. Handle explicit 'attributes' column from Excel (Manual Add)
        if row and ('attributes' in row or 'attributes ' in row): # Check both just in case
            val = row.get('attributes') or row.get('attributes ')
            if val and str(val).strip().lower() not in ['none', 'null', '']:
                clean_val = str(val).split(';')
                for raw_name in clean_val:
                    name = raw_name.strip()
                    if name:
                        attr_obj, _ = Attribute.objects.get_or_create(name=name)
                        instance.attributes.add(attr_obj)

        # 2. PULL: Inherit attributes from Ancestors
        # Walk up the tree? Or just parent. If parent has it, it implies parent got it from grandparent.
        if instance.parent:
            parent_attrs = instance.parent.attributes.all()
            for attr in parent_attrs:
                instance.attributes.add(attr)
        
        # 3. PUSH: Propagate to ALL Descendants (Recursive)
        # We need to define a helper function to walk down the tree
        def propagate_down(category, attributes_to_add):
            children = category.children.all()
            for child in children:
                for attr in attributes_to_add:
                    child.attributes.add(attr)
                # Recurse
                propagate_down(child, attributes_to_add)

        my_attrs = instance.attributes.all()
        if my_attrs.exists():
            propagate_down(instance, my_attrs)


class ProductResource(resources.ModelResource):
    category = fields.Field(
        column_name='category',
        attribute='category',
        widget=ForeignKeyWidget(Category, 'name')
    )
    # Exclude cover_image from automatic mapping to handle URL download manually
    # We will handle 'cover_image' in hooks

    class Meta:
        model = Product
        import_id_fields = ('name',) 
        fields = ('id', 'category', 'name', 'slug', 'price', 'discount_percentage', 'stock', 'description', 'is_active')
        skip_unchanged = True
        report_skipped = True

    def before_import_row(self, row, **kwargs):
        # Auto-generate slug
        if 'name' in row and ('slug' not in row or not row['slug']):
            from django.utils.text import slugify
            from unidecode import unidecode
            row['slug'] = slugify(unidecode(row['name']))
        
        pass

    def before_save_instance(self, instance, row, **kwargs):
        # Handle Cover Image (URL or Local Path)
        img_path = row.get('cover_image')
        if img_path:
            import os
            import requests
            from django.core.files.base import ContentFile, File
            
            path_str = str(img_path).strip()
            
            # Helper to generate filename
            file_name = path_str.split("/")[-1].split("\\")[-1]
            if not file_name or '.' not in file_name:
                file_name = f"{instance.slug}.jpg"

            # Case A: Online URL
            if path_str.lower().startswith(('http://', 'https://')):
                try:
                    response = requests.get(path_str, timeout=10)
                    if response.status_code == 200:
                        instance.cover_image.save(file_name, ContentFile(response.content), save=False)
                except Exception:
                    pass 
            
            # Case B: Local File Path
            elif os.path.exists(path_str) and os.path.isfile(path_str):
                try:
                    with open(path_str, 'rb') as f:
                        instance.cover_image.save(file_name, File(f), save=False)
                except Exception:
                    pass

    def after_save_instance(self, instance, row=None, **kwargs):
        if not row: return
        import os
        import requests
        from django.core.files.base import ContentFile, File

        # 1. Handle Attributes Values: "Màu sắc:Đỏ; Kích thước:XL"
        # Column header: 'attributes-values'
        attrs_str = row.get('attributes-values')
        if attrs_str:
            pairs = str(attrs_str).split(';')
            for pair in pairs:
                if ':' in pair:
                    attr_name, val = pair.split(':', 1)
                    attr_name = attr_name.strip()
                    val = val.strip()
                    if attr_name and val:
                        # Find or create Attribute
                        attr_obj, _ = Attribute.objects.get_or_create(name=attr_name)
                        # Create Value
                        ProductAttributeValue.objects.update_or_create(
                            product=instance,
                            attribute=attr_obj,
                            defaults={'value': val}
                        )
        
        # 2. Handle Album Images: "path1; path2"
        # Column header: 'image'
        album_str = row.get('image')
        if album_str:
            paths = str(album_str).split(';')
            for idx, path_val in enumerate(paths):
                path_val = path_val.strip()
                if not path_val: continue

                fname = path_val.split("/")[-1].split("\\")[-1]
                if not fname or '.' not in fname:
                    fname = f"{instance.slug}_album_{idx}.jpg"

                # Prepare content
                content = None
                
                # Try URL
                if path_val.lower().startswith(('http://', 'https://')):
                    try:
                        res = requests.get(path_val, timeout=10)
                        if res.status_code == 200:
                            content = ContentFile(res.content)
                    except:
                        pass
                # Try Local File
                elif os.path.exists(path_val) and os.path.isfile(path_val):
                    try:
                        with open(path_val, 'rb') as f:
                            # Must read content to ContentFile because 'f' closes after with block
                            content = ContentFile(f.read()) 
                    except:
                        pass
                
                # Save if we got content
                if content:
                    p_img = ProductImage(product=instance)
                    p_img.image.save(fname, content, save=True)


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
