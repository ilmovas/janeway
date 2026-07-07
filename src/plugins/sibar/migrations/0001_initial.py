from django.db import migrations, models
import django.db.models.deletion
import django.utils.timezone


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        ("submission", "0001_initial"),
    ]

    operations = [
        migrations.CreateModel(
            name="SibarCheck",
            fields=[
                ("id", models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name="ID")),
                ("article", models.ForeignKey(
                    on_delete=django.db.models.deletion.CASCADE,
                    related_name="sibar_checks",
                    to="submission.article",
                )),
                ("status", models.CharField(
                    choices=[
                        ("pending", "Pending"),
                        ("submitted", "Submitted"),
                        ("processing", "Processing"),
                        ("complete", "Complete"),
                        ("error", "Error"),
                    ],
                    default="pending",
                    max_length=16,
                )),
                ("external_job_id", models.CharField(blank=True, max_length=255, null=True)),
                ("language_score", models.DecimalField(
                    blank=True, decimal_places=2, max_digits=5, null=True,
                    help_text="Overall language quality score (0-100).",
                )),
                ("grammar_issues", models.PositiveIntegerField(blank=True, null=True)),
                ("spelling_issues", models.PositiveIntegerField(blank=True, null=True)),
                ("style_issues", models.PositiveIntegerField(blank=True, null=True)),
                ("report_url", models.URLField(blank=True, null=True)),
                ("raw_response", models.JSONField(blank=True, null=True)),
                ("error_message", models.TextField(blank=True, null=True)),
                ("date_submitted", models.DateTimeField(default=django.utils.timezone.now)),
                ("date_completed", models.DateTimeField(blank=True, null=True)),
            ],
            options={"ordering": ["-date_submitted"]},
        ),
    ]
