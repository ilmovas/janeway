from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ("sibar", "0003_researcher_profile"),
    ]

    operations = [
        migrations.RemoveField(
            model_name="sibarcheck",
            name="report_url",
        ),
    ]
