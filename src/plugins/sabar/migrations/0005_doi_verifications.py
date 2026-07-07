from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("sabar", "0004_remove_report_url"),
    ]

    operations = [
        migrations.AddField(
            model_name="sabarcheck",
            name="doi_verifications",
            field=models.JSONField(blank=True, null=True),
        ),
    ]
