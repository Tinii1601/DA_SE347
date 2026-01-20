from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = []

    operations = [
        migrations.CreateModel(
            name="Store",
            fields=[
                ("id", models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name="ID")),
                ("name", models.CharField(max_length=150, verbose_name="Tên cửa hàng")),
                ("address", models.CharField(max_length=255, verbose_name="Địa chỉ")),
                ("city", models.CharField(blank=True, max_length=100, verbose_name="Tỉnh/Thành phố")),
                ("map_url", models.URLField(blank=True, verbose_name="Link bản đồ")),
                ("opening_hours", models.CharField(blank=True, max_length=100, verbose_name="Giờ mở cửa")),
                ("description", models.TextField(blank=True, verbose_name="Mô tả")),
                ("image", models.ImageField(blank=True, null=True, upload_to="stores/", verbose_name="Ảnh cửa hàng")),
                ("is_active", models.BooleanField(default=True, verbose_name="Hiển thị")),
                ("display_order", models.PositiveIntegerField(default=0, verbose_name="Thứ tự hiển thị")),
                ("created_at", models.DateTimeField(auto_now_add=True)),
            ],
            options={
                "verbose_name": "Cửa hàng",
                "verbose_name_plural": "Hệ thống cửa hàng",
                "ordering": ["display_order", "-created_at"],
            },
        ),
    ]
