from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("sabar", "0002_update_sibar_fields"),
    ]

    operations = [
        migrations.AddField(
            model_name="sabarcheck",
            name="researcher_profile",
            field=models.JSONField(blank=True, null=True),
        ),
    ]
