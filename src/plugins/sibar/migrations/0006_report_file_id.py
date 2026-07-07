from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("sibar", "0005_doi_verifications"),
    ]

    operations = [
        migrations.AddField(
            model_name="sibarcheck",
            name="report_file_id",
            field=models.IntegerField(blank=True, null=True),
        ),
    ]
