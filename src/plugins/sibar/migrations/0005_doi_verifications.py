from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("sibar", "0004_remove_report_url"),
    ]

    operations = [
        migrations.AddField(
            model_name="sibarcheck",
            name="doi_verifications",
            field=models.JSONField(blank=True, null=True),
        ),
    ]
