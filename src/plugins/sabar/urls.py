from django.urls import path

from plugins.sabar import views

urlpatterns = [
    path("", views.manager, name="sabar_index"),
    path("articles/", views.articles, name="sabar_articles"),
    path("articles/submit-all/", views.submit_all, name="sabar_submit_all"),
    path("articles/<int:article_id>/", views.article, name="sabar_article"),
    path("articles/<int:article_id>/submit/", views.submit_check, name="sabar_submit"),
    path("articles/<int:article_id>/refresh/", views.refresh_check, name="sabar_refresh"),
    path("articles/<int:article_id>/analyze/", views.deep_analysis, name="sabar_analyze"),
    path("articles/<int:article_id>/verify-refs/", views.verify_references, name="sabar_verify_refs"),
    path("articles/<int:article_id>/report/", views.generate_report, name="sabar_generate_report"),
    path("articles/<int:article_id>/report/download/", views.download_report, name="sabar_download_report"),
    path("articles/<int:article_id>/complete/", views.complete, name="sabar_complete"),
]
