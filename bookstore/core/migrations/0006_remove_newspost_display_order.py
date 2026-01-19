from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ("core", "0005_newspost_display_order"),
    ]

    operations = [
        migrations.RemoveField(
            model_name="newspost",
            name="display_order",
        ),
    ]
