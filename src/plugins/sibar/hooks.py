from django.urls import reverse
from django.utils.html import format_html


def article_task_hook(context):
    article = context.get("article")
    if not article:
        return ""

    check = article.sibar_checks.first()
    if not check:
        return ""

    url = reverse("sibar_article", kwargs={"article_id": article.pk})
    label = "Sibar: {}".format(check.get_status_display())
    return format_html(
        '<li><a href="{}"><i class="fa fa-language"></i> {}</a></li>',
        url,
        label,
    )
