from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ("sabar", "0003_researcher_profile"),
    ]

    operations = [
        migrations.RemoveField(
            model_name="sabarcheck",
            name="report_url",
        ),
    ]
