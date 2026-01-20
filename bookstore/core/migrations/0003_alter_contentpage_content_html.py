from django.db import migrations
import ckeditor_uploader.fields


class Migration(migrations.Migration):

    dependencies = [
        ("core", "0002_contentpage"),
    ]

    operations = [
        migrations.AlterField(
            model_name="contentpage",
            name="content_html",
            field=ckeditor_uploader.fields.RichTextUploadingField(),
        ),
    ]
