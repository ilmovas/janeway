from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("sabar", "0005_doi_verifications"),
    ]

    operations = [
        migrations.AddField(
            model_name="sabarcheck",
            name="report_file_id",
            field=models.IntegerField(blank=True, null=True),
        ),
    ]
