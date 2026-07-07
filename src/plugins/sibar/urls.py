from django.urls import path

from plugins.sibar import views

urlpatterns = [
    path("", views.manager, name="sibar_index"),
    path("articles/", views.articles, name="sibar_articles"),
    path("articles/submit-all/", views.submit_all, name="sibar_submit_all"),
    path("articles/<int:article_id>/", views.article, name="sibar_article"),
    path("articles/<int:article_id>/submit/", views.submit_check, name="sibar_submit"),
    path("articles/<int:article_id>/refresh/", views.refresh_check, name="sibar_refresh"),
    path("articles/<int:article_id>/analyze/", views.deep_analysis, name="sibar_analyze"),
    path("articles/<int:article_id>/verify-refs/", views.verify_references, name="sibar_verify_refs"),
    path("articles/<int:article_id>/report/", views.generate_report, name="sibar_generate_report"),
    path("articles/<int:article_id>/report/download/", views.download_report, name="sibar_download_report"),
    path("articles/<int:article_id>/complete/", views.complete, name="sibar_complete"),
]
