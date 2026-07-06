from django.db import models
from django.utils import timezone

from submission.models import Article

STATUS_PENDING = "pending"
STATUS_COMPLETE = "complete"
STATUS_ERROR = "error"

STATUS_CHOICES = [
    (STATUS_PENDING, "Pending"),
    (STATUS_COMPLETE, "Complete"),
    (STATUS_ERROR, "Error"),
]

VERDICT_CONFIRMED = "confirmed"
VERDICT_SUSPECTED = "suspected"
VERDICT_SIMILAR = "similar"
VERDICT_CLEAN = "clean"

# Threshold labels mirror GET /api/v1/check/verdicts (confirmed 0.98, suspected 0.95, similar 0.90).
VERDICT_CHOICES = [
    (VERDICT_CONFIRMED, "Confirmed Duplicate (≥ 0.98)"),
    (VERDICT_SUSPECTED, "Suspected Duplicate (≥ 0.95)"),
    (VERDICT_SIMILAR, "Similar (≥ 0.90)"),
    (VERDICT_CLEAN, "Clean (< 0.90)"),
]


class SabarCheck(models.Model):
    article = models.ForeignKey(
        Article, on_delete=models.CASCADE, related_name="sabar_checks"
    )
    status = models.CharField(
        max_length=16, choices=STATUS_CHOICES, default=STATUS_PENDING
    )

    # IDs from Sibar API
    report_id = models.CharField(max_length=255, blank=True, null=True)

    # Core result fields from POST /api/v1/check response
    is_duplicate = models.BooleanField(null=True, blank=True)
    confidence = models.DecimalField(
        max_digits=5, decimal_places=4, blank=True, null=True,
        help_text="Similarity confidence score (0.0 – 1.0).",
    )
    verdict = models.CharField(
        max_length=16, choices=VERDICT_CHOICES, blank=True, null=True
    )
    integrity_score = models.DecimalField(
        max_digits=5, decimal_places=2, blank=True, null=True,
        help_text="Overall integrity score (0–100).",
    )
    recommendation = models.TextField(blank=True, null=True)
    verdict_ar = models.CharField(max_length=255, blank=True, null=True)
    verdict_en = models.CharField(max_length=255, blank=True, null=True)

    # Matches list from the response
    matches = models.JSONField(blank=True, null=True)
    reasons = models.JSONField(blank=True, null=True)

    # Deep analysis (POST /api/v1/analyze)
    deep_analysis = models.JSONField(blank=True, null=True)

    raw_response = models.JSONField(blank=True, null=True)
    researcher_profile = models.JSONField(blank=True, null=True)
    error_message = models.TextField(blank=True, null=True)

    date_submitted = models.DateTimeField(default=timezone.now)
    date_completed = models.DateTimeField(blank=True, null=True)

    class Meta:
        ordering = ["-date_submitted"]

    def __str__(self):
        return "SibarCheck #{} — {}".format(self.pk, self.article)

    @property
    def confidence_percent(self):
        if self.confidence is None:
            return None
        return round(float(self.confidence) * 100, 1)

    @property
    def is_flagged(self):
        return self.verdict in (VERDICT_CONFIRMED, VERDICT_SUSPECTED)

    @property
    def verdict_badge_class(self):
        return {
            VERDICT_CONFIRMED: "alert",
            VERDICT_SUSPECTED: "warning",
            VERDICT_SIMILAR: "secondary",
            VERDICT_CLEAN: "success",
        }.get(self.verdict, "secondary")

    @property
    def online_matches(self):
        raw = self.raw_response or {}
        sig = raw.get("layer0_signals") or {}
        return sig.get("results") or []

    @property
    def has_online_similarity(self):
        return len(self.online_matches) > 0

    @property
    def researcher(self):
        raw = self.raw_response or {}
        # prefer explicitly stored field, fall back to raw_response embed
        return self.researcher_profile or raw.get("researcher_profile") or None
