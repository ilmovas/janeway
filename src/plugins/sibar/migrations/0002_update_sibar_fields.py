from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("sibar", "0001_initial"),
    ]

    operations = [
        migrations.RemoveField(model_name="sibarcheck", name="external_job_id"),
        migrations.RemoveField(model_name="sibarcheck", name="language_score"),
        migrations.RemoveField(model_name="sibarcheck", name="grammar_issues"),
        migrations.RemoveField(model_name="sibarcheck", name="spelling_issues"),
        migrations.RemoveField(model_name="sibarcheck", name="style_issues"),
        migrations.AddField(
            model_name="sibarcheck",
            name="report_id",
            field=models.CharField(blank=True, max_length=255, null=True),
        ),
        migrations.AddField(
            model_name="sibarcheck",
            name="is_duplicate",
            field=models.BooleanField(blank=True, null=True),
        ),
        migrations.AddField(
            model_name="sibarcheck",
            name="confidence",
            field=models.DecimalField(
                blank=True, decimal_places=4, max_digits=5, null=True,
                help_text="Similarity confidence score (0.0 – 1.0).",
            ),
        ),
        migrations.AddField(
            model_name="sibarcheck",
            name="verdict",
            field=models.CharField(
                blank=True,
                choices=[
                    ("confirmed", "Confirmed Duplicate (≥ 0.98)"),
                    ("suspected", "Suspected Duplicate (≥ 0.95)"),
                    ("similar", "Similar (≥ 0.90)"),
                    ("clean", "Clean (< 0.90)"),
                ],
                max_length=16,
                null=True,
            ),
        ),
        migrations.AddField(
            model_name="sibarcheck",
            name="integrity_score",
            field=models.DecimalField(
                blank=True, decimal_places=2, max_digits=5, null=True,
                help_text="Overall integrity score (0–100).",
            ),
        ),
        migrations.AddField(
            model_name="sibarcheck",
            name="recommendation",
            field=models.TextField(blank=True, null=True),
        ),
        migrations.AddField(
            model_name="sibarcheck",
            name="verdict_ar",
            field=models.CharField(blank=True, max_length=255, null=True),
        ),
        migrations.AddField(
            model_name="sibarcheck",
            name="verdict_en",
            field=models.CharField(blank=True, max_length=255, null=True),
        ),
        migrations.AddField(
            model_name="sibarcheck",
            name="matches",
            field=models.JSONField(blank=True, null=True),
        ),
        migrations.AddField(
            model_name="sibarcheck",
            name="reasons",
            field=models.JSONField(blank=True, null=True),
        ),
        migrations.AddField(
            model_name="sibarcheck",
            name="deep_analysis",
            field=models.JSONField(blank=True, null=True),
        ),
        migrations.AlterField(
            model_name="sibarcheck",
            name="status",
            field=models.CharField(
                choices=[
                    ("pending", "Pending"),
                    ("complete", "Complete"),
                    ("error", "Error"),
                ],
                default="pending",
                max_length=16,
            ),
        ),
    ]
