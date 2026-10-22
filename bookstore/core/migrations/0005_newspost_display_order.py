from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("core", "0004_newspost"),
    ]

    operations = [
        migrations.SeparateDatabaseAndState(
            state_operations=[
                migrations.AddField(
                    model_name="newspost",
                    name="display_order",
                    field=models.PositiveIntegerField(default=0),
                ),
            ],
            database_operations=[]
        ),
    ]
