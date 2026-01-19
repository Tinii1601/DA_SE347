from django.db import migrations, models
import ckeditor_uploader.fields


class Migration(migrations.Migration):

    dependencies = [
        ("core", "0003_alter_contentpage_content_html"),
    ]

    operations = [
        migrations.CreateModel(
            name="NewsPost",
            fields=[
                ("id", models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name="ID")),
                ("title", models.CharField(max_length=200)),
                ("slug", models.SlugField(blank=True, max_length=200, unique=True)),
                ("summary", models.CharField(blank=True, max_length=300)),
                ("body_html", ckeditor_uploader.fields.RichTextUploadingField()),
                ("cover_image", models.ImageField(blank=True, null=True, upload_to="news/")),
                (
                    "category",
                    models.CharField(
                        choices=[("promo", "Ưu đãi"), ("event", "Sự kiện")], max_length=20
                    ),
                ),
                ("published_at", models.DateField(blank=True, null=True)),
                ("is_active", models.BooleanField(default=True)),
                ("display_order", models.PositiveIntegerField(default=0)),
                ("created_at", models.DateTimeField(auto_now_add=True)),
                ("updated_at", models.DateTimeField(auto_now=True)),
            ],
            options={
                "ordering": ["display_order", "-published_at", "-created_at"],
            },
        ),
    ]
