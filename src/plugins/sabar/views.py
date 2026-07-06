from django.contrib import messages
from django.shortcuts import get_object_or_404, redirect, render
from django.utils import timezone

from plugins.sabar import plugin_settings
from plugins.sabar.api_client import (
    SibarAPIError,
    fetch_result,
    health_check,
    run_deep_analysis,
    submit_article,
)
from plugins.sabar.models import SabarCheck, STATUS_COMPLETE, STATUS_ERROR
from security.decorators import editor_user_required
from submission.models import Article
from events import logic as events_logic


@editor_user_required
def manager(request):
    from utils import setting_handler
    from plugins.sabar.api_client import _get_plugin

    plugin = _get_plugin()

    def _get(name):
        try:
            return setting_handler.get_plugin_setting(plugin, name, request.journal, create=True).value or ""
        except Exception:
            return ""

    if request.method == "POST":
        save_ok = True
        for name in ["sabar_api_url", "sabar_api_key"]:
            value = request.POST.get(name, "").strip()
            if name == "sabar_api_key" and not value:
                continue
            try:
                sv = setting_handler.get_plugin_setting(plugin, name, request.journal, create=True)
                sv.value = value
                sv.save()
            except Exception as exc:
                save_ok = False
                messages.error(request, "خطأ في حفظ {}: {}".format(name, exc))
        if save_ok:
            messages.success(request, "تم حفظ الإعدادات بنجاح.")
        return redirect("sabar_index")

    current = {
        "sabar_api_url": _get("sabar_api_url"),
        "sabar_api_key": _get("sabar_api_key"),
    }
    healthy = health_check(request.journal)
    return render(request, "sabar/manager.html", {
        "plugin": plugin_settings,
        "api_healthy": healthy,
        "current": current,
    })


@editor_user_required
def articles(request):
    article_list = Article.objects.filter(
        journal=request.journal
    ).prefetch_related("sabar_checks").order_by("-date_submitted")
    return render(request, "sabar/articles.html", {"articles": article_list})


@editor_user_required
def article(request, article_id):
    art = get_object_or_404(Article, pk=article_id, journal=request.journal)
    check = art.sabar_checks.first()
    return render(request, "sabar/article.html", {"article": art, "check": check})


@editor_user_required
def submit_all(request):
    """Submit all journal articles to Sibar in one go."""
    if request.method == "POST":
        arts = Article.objects.filter(journal=request.journal)
        ok = 0
        errors = 0
        for art in arts:
            try:
                report_id, data = submit_article(art)
                SabarCheck.objects.create(
                    article=art,
                    status=STATUS_COMPLETE,
                    report_id=report_id,
                    is_duplicate=data.get("is_duplicate"),
                    confidence=data.get("confidence"),
                    verdict=data.get("verdict"),
                    integrity_score=data.get("integrity_score"),
                    recommendation=data.get("recommendation"),
                    verdict_ar=data.get("verdict_ar"),
                    verdict_en=data.get("verdict_en"),
                    matches=data.get("matches"),
                    reasons=data.get("reasons"),
                    researcher_profile=data.get("researcher_profile"),
                    raw_response=data,
                    date_completed=timezone.now(),
                )
                ok += 1
            except SibarAPIError as exc:
                errors += 1
        if ok:
            messages.success(request, "تم فحص {} مقال بنجاح.".format(ok))
        if errors:
            messages.warning(request, "فشل فحص {} مقال — تحقق من إعدادات API.".format(errors))
    return redirect("sabar_articles")


@editor_user_required
def submit_check(request, article_id):
    art = get_object_or_404(Article, pk=article_id, journal=request.journal)
    if request.method == "POST":
        try:
            report_id, data = submit_article(art)
            check = SabarCheck.objects.create(
                article=art,
                status=STATUS_COMPLETE,
                report_id=report_id,
                is_duplicate=data.get("is_duplicate"),
                confidence=data.get("confidence"),
                verdict=data.get("verdict"),
                integrity_score=data.get("integrity_score"),
                recommendation=data.get("recommendation"),
                verdict_ar=data.get("verdict_ar"),
                verdict_en=data.get("verdict_en"),
                matches=data.get("matches"),
                reasons=data.get("reasons"),
                researcher_profile=data.get("researcher_profile"),
                raw_response=data,
                date_completed=timezone.now(),
            )
            messages.success(
                request,
                "Sibar check completed — verdict: {}.".format(
                    check.get_verdict_display() or check.verdict
                ),
            )
        except SibarAPIError as exc:
            messages.error(request, "Sibar error: {}".format(exc))
    return redirect("sabar_article", article_id=article_id)


@editor_user_required
def refresh_check(request, article_id):
    """Fetch report data from GET /api/v1/reports/{report_id}/data."""
    art = get_object_or_404(Article, pk=article_id, journal=request.journal)
    check = art.sabar_checks.first()
    if request.method == "POST" and check and check.report_id:
        try:
            data = fetch_result(request.journal, check.report_id)
            check.raw_response = data
            check.is_duplicate = data.get("is_duplicate", check.is_duplicate)
            if data.get("confidence") is not None:
                check.confidence = data.get("confidence")
            check.verdict = data.get("verdict", check.verdict)
            if data.get("integrity_score") is not None:
                check.integrity_score = data.get("integrity_score")
            check.recommendation = data.get("recommendation", check.recommendation)
            check.verdict_ar = data.get("verdict_ar", check.verdict_ar)
            check.verdict_en = data.get("verdict_en", check.verdict_en)
            check.reasons = data.get("reasons", check.reasons)
            l1 = data.get("layer1_signals")
            if l1 and not check.researcher_profile:
                check.researcher_profile = l1
            check.save()
            messages.success(request, "Report data refreshed from Sibar.")
        except SibarAPIError as exc:
            messages.error(request, "Sibar error: {}".format(exc))
    return redirect("sabar_article", article_id=article_id)


@editor_user_required
def deep_analysis(request, article_id):
    """POST /api/v1/analyze — protected, requires API key."""
    art = get_object_or_404(Article, pk=article_id, journal=request.journal)
    check = art.sabar_checks.first()
    if request.method == "POST" and check:
        try:
            data = run_deep_analysis(request.journal, art)
            check.deep_analysis = data
            check.save()
            messages.success(request, "Deep analysis completed.")
        except SibarAPIError as exc:
            messages.error(request, "Sibar error: {}".format(exc))
    return redirect("sabar_article", article_id=article_id)


@editor_user_required
def complete(request, article_id):
    art = get_object_or_404(Article, pk=article_id, journal=request.journal)
    if request.method == "POST":
        events_logic.Events.raise_event(
            events_logic.Events.ON_WORKFLOW_ELEMENT_COMPLETE,
            handshake_url=plugin_settings.HANDSHAKE_URL,
            article=art,
            request=request,
            user=request.user,
        )
        return redirect("core_dashboard")
    return redirect("sabar_article", article_id=article_id)
