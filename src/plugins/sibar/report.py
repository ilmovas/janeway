"""Official Sibar integrity report PDF generator (WeasyPrint, Arabic RTL)."""

from __future__ import annotations

import base64
import html
import os
from decimal import Decimal

_PLUGIN_DIR = os.path.dirname(os.path.abspath(__file__))
_TAJAWAL_400 = os.path.join(_PLUGIN_DIR, "assets", "fonts", "tajawal-400.ttf")
_TAJAWAL_700 = os.path.join(_PLUGIN_DIR, "assets", "fonts", "tajawal-700.ttf")

_RECOMMENDATION_AR = {
    "accept": "قبول النشر",
    "reject": "رفض النشر",
    "review": "يحتاج مراجعة",
}

_SALAMI_AR = {
    "high": "عالية",
    "medium": "متوسطة",
    "low": "منخفضة",
}


def _load_font_b64(path: str) -> str:
    if not os.path.exists(path):
        return ""
    with open(path, "rb") as fh:
        return base64.b64encode(fh.read()).decode()


def _esc(value) -> str:
    if value is None:
        return "—"
    return html.escape(str(value))


def _score_color(score) -> str:
    val = float(score or 0)
    if val >= 75:
        return "#1B4D3E"
    if val >= 50:
        return "#C9A84C"
    return "#C0392B"


def _report_id_short(report_id) -> str:
    if not report_id:
        return "—"
    if len(report_id) <= 12:
        return report_id
    return report_id[:8] + "…"


def _fmt_date(dt) -> str:
    if not dt:
        return "—"
    try:
        return dt.strftime("%Y-%m-%d %H:%M")
    except AttributeError:
        return _esc(dt)


def _fmt_score(score) -> str:
    if score is None:
        return "—"
    if isinstance(score, Decimal):
        return str(int(score)) if score == int(score) else str(score)
    val = float(score)
    return str(int(val)) if val == int(val) else str(round(val, 1))


def _similarity_pct(match) -> str:
    sim = match.get("similarity")
    if sim is None:
        return "—"
    return "{}%".format(round(float(sim) * 100, 1))


def _match_url(match) -> str:
    return match.get("url") or match.get("link") or ""


def generate_report_pdf(check) -> bytes:
    """Build the official journal-branded integrity report and return PDF bytes."""
    from weasyprint import HTML

    article = check.article
    journal = article.journal
    score = check.integrity_score
    color = _score_color(score)

    font_400 = _load_font_b64(_TAJAWAL_400)
    font_700 = _load_font_b64(_TAJAWAL_700)
    body_font_family = "Tajawal, sans-serif" if (font_400 and font_700) else "sans-serif"
    font_css = ""
    if font_400 and font_700:
        font_css = """
@font-face {{
  font-family: Tajawal;
  font-weight: 400;
  src: url(data:font/ttf;base64,{font_400}) format('truetype');
}}
@font-face {{
  font-family: Tajawal;
  font-weight: 700;
  src: url(data:font/ttf;base64,{font_700}) format('truetype');
}}
""".format(font_400=font_400, font_700=font_700)

    online = check.online_matches or []
    researcher = check.researcher
    refs = check.reference_results or []
    ref_integrity = check.reference_integrity
    reasons = check.reasons or []

    rec_ar = _RECOMMENDATION_AR.get(check.recommendation or "", check.recommendation or "")

    reasons_html = ""
    for reason in reasons:
        reasons_html += "<li>⚠ {}</li>".format(_esc(reason))

    online_html = ""
    if online:
        rows = ""
        for match in online:
            url = _match_url(match)
            source = _esc(match.get("source") or url or "—")
            title = _esc(match.get("title"))
            link_cell = (
                '<a href="{}">{}</a>'.format(html.escape(url, quote=True), source)
                if url
                else source
            )
            rows += (
                "<tr><td>{}</td><td>{}</td><td>{}</td><td>{}</td></tr>".format(
                    _similarity_pct(match),
                    title,
                    source,
                    link_cell,
                )
            )
        online_html = """
        <div class="section">
          <h2>المصادر المرصودة على الإنترنت</h2>
          <table class="data-table">
            <thead><tr>
              <th>نسبة التشابه</th><th>العنوان</th><th>المصدر</th><th>الرابط</th>
            </tr></thead>
            <tbody>{rows}</tbody>
          </table>
        </div>
        """.format(rows=rows)

    researcher_html = ""
    if researcher:
        salami = researcher.get("salami_risk") or ""
        salami_ar = _SALAMI_AR.get(salami, salami or "—")
        signals_html = ""
        for signal in researcher.get("salami_signals") or []:
            sev = signal.get("severity") or ""
            sev_ar = _SALAMI_AR.get(sev, sev)
            signals_html += "<li>{} <span class=\"badge\">{}</span></li>".format(
                _esc(signal.get("description")),
                _esc(sev_ar) if sev_ar else "",
            )
        signals_block = ""
        if signals_html:
            signals_block = (
                "<h3>مؤشرات التقطيع البحثي</h3><ul class=\"signals\">"
                + signals_html
                + "</ul>"
            )
        researcher_html = """
        <div class="section">
          <h2>السجل البحثي للمؤلف</h2>
          <table class="info-table">
            <tr><td class="label">الاسم</td><td>{name}</td></tr>
            <tr><td class="label">عدد المنشورات</td><td>{pubs}</td></tr>
            <tr><td class="label">معدل النشر السنوي</td><td>{rate}</td></tr>
            <tr><td class="label">الأبحاث المسحوبة</td><td>{retractions}</td></tr>
            <tr><td class="label">مخاطر التقطيع البحثي</td><td>{salami}</td></tr>
          </table>
          {signals}
        </div>
        """.format(
            name=_esc(researcher.get("name")),
            pubs=_esc(researcher.get("total_publications")),
            rate=_esc(researcher.get("annual_pub_rate")),
            retractions=_esc(researcher.get("retraction_count")),
            salami=_esc(salami_ar),
            signals=signals_block,
        )

    refs_html = ""
    if refs and ref_integrity:
        ref_rows = ""
        for ref in refs:
            if ref.get("is_retracted"):
                status = "محذوف"
            elif ref.get("exists"):
                status = "موثّق"
            else:
                status = "غير موجود"
            ref_rows += (
                "<tr><td class=\"ltr\">{}</td><td>{}</td><td>{}</td>"
                "<td>{}</td></tr>".format(
                    _esc(ref.get("doi")),
                    status,
                    _esc(ref.get("title")),
                    _esc(ref.get("journal")),
                )
            )
        refs_html = """
        <div class="section">
          <h2>سلامة المراجع</h2>
          <p class="summary">
            نسبة السلامة: <strong>{pct}%</strong>
            — موثّقة {verified} من {total}
          </p>
          <table class="data-table">
            <thead><tr>
              <th>DOI</th><th>الحالة</th><th>العنوان</th><th>المجلة</th>
            </tr></thead>
            <tbody>{rows}</tbody>
          </table>
        </div>
        """.format(
            pct=ref_integrity.get("pct", 0),
            verified=ref_integrity.get("verified", 0),
            total=ref_integrity.get("total", 0),
            rows=ref_rows,
        )

    html_doc = """<!DOCTYPE html>
<html lang="ar" dir="rtl">
<head>
<meta charset="UTF-8">
<style>
{font_css}
@page {{ size: A4; margin: 18mm 16mm 22mm 16mm; }}
body {{
  font-family: {body_font_family};
  font-size: 11pt;
  color: #0F1F1A;
  direction: rtl;
  line-height: 1.55;
}}
.header {{
  background: #1B4D3E;
  color: #fff;
  padding: 1.25rem 1.5rem;
  border-radius: 8px 8px 0 0;
  text-align: center;
}}
.header h1 {{
  font-weight: 700;
  font-size: 1.35rem;
  margin: 0 0 0.35rem;
}}
.header .subtitle {{
  color: #E8D5A3;
  font-size: 0.95rem;
  margin: 0;
}}
.gold-line {{ height: 3px; background: #C9A84C; }}
.body {{ padding: 1.25rem 0.25rem; }}
.meta {{
  display: table;
  width: 100%;
  background: #F9F7F2;
  border-radius: 6px;
  padding: 0.75rem 1rem;
  margin-bottom: 1.25rem;
}}
.meta-row {{ display: table-row; }}
.meta-item {{
  display: table-cell;
  width: 33%;
  text-align: center;
  vertical-align: top;
  padding: 0.35rem;
}}
.meta-label {{ font-size: 0.75rem; color: #4A6358; }}
.meta-value {{ font-weight: 700; color: #1B4D3E; font-size: 0.9rem; }}
.score-card {{
  border: 3px solid {color};
  border-radius: 10px;
  padding: 1.25rem;
  text-align: center;
  margin-bottom: 1.25rem;
  background: #fff;
}}
.score-card h2 {{ font-size: 1rem; margin: 0 0 0.75rem; color: #1B4D3E; }}
.score-number {{
  font-size: 3rem;
  font-weight: 700;
  color: {color};
  line-height: 1;
}}
.score-number span {{ font-size: 1.1rem; font-weight: 500; opacity: 0.75; }}
.verdict-ar {{ font-size: 1.2rem; font-weight: 700; color: {color}; margin: 0.75rem 0 0.25rem; }}
.verdict-en {{ font-size: 0.9rem; color: #4A6358; }}
.rec-badge {{
  display: inline-block;
  margin-top: 0.5rem;
  padding: 0.2rem 0.75rem;
  border-radius: 4px;
  background: #F9F7F2;
  border: 1px solid #C9A84C;
  font-size: 0.85rem;
}}
.reasons {{
  list-style: none;
  margin: 1rem 0 0;
  padding: 0;
  text-align: right;
}}
.reasons li {{
  padding: 0.35rem 0.5rem;
  margin-bottom: 0.25rem;
  background: rgba(0,0,0,0.04);
  border-radius: 4px;
  font-size: 0.9rem;
}}
.section {{ margin-bottom: 1.25rem; page-break-inside: avoid; }}
.section h2 {{
  font-size: 1.05rem;
  color: #1B4D3E;
  border-bottom: 2px solid #C9A84C;
  padding-bottom: 0.35rem;
  margin: 0 0 0.75rem;
}}
.section h3 {{ font-size: 0.95rem; margin: 0.75rem 0 0.35rem; }}
.info-table, .data-table {{
  width: 100%;
  border-collapse: collapse;
  font-size: 0.88rem;
}}
.info-table td {{
  padding: 0.35rem 0.5rem;
  border-bottom: 1px solid #E8E8E8;
}}
.info-table .label {{
  color: #4A6358;
  width: 38%;
  font-weight: 500;
}}
.data-table th, .data-table td {{
  padding: 0.4rem 0.45rem;
  border: 1px solid #E8E8E8;
  text-align: right;
}}
.data-table th {{
  background: #F9F7F2;
  color: #1B4D3E;
  font-weight: 700;
}}
.data-table a {{ color: #1B4D3E; word-break: break-all; }}
.ltr {{ direction: ltr; text-align: left; font-family: monospace; font-size: 0.82rem; }}
.summary {{ margin-bottom: 0.75rem; }}
.signals {{ margin: 0; padding-right: 1.25rem; }}
.signals .badge {{ font-size: 0.8rem; color: #8B6914; }}
.footer {{
  margin-top: 1.5rem;
  padding-top: 0.75rem;
  border-top: 1px solid #E8E8E8;
  font-size: 0.8rem;
  color: #4A6358;
  text-align: center;
}}
.footer .disclaimer {{ margin-bottom: 0.5rem; }}
.footer .service {{ font-size: 0.75rem; color: #8B6914; }}
</style>
</head>
<body>
  <div class="header">
    <h1>{journal_name}</h1>
    <p class="subtitle">تقرير النزاهة البحثية</p>
  </div>
  <div class="gold-line"></div>
  <div class="body">
    <div class="meta">
      <div class="meta-row">
        <div class="meta-item">
          <div class="meta-label">رقم التقرير</div>
          <div class="meta-value">{report_id}</div>
        </div>
        <div class="meta-item">
          <div class="meta-label">تاريخ الفحص</div>
          <div class="meta-value">{date}</div>
        </div>
        <div class="meta-item">
          <div class="meta-label">عنوان المقال</div>
          <div class="meta-value">{article_title}</div>
        </div>
      </div>
    </div>

    <div class="score-card">
      <h2>درجة النزاهة البحثية</h2>
      <div class="score-number">{score}<span>/100</span></div>
      <div class="verdict-ar">{verdict_ar}</div>
      <div class="verdict-en">{verdict_en}</div>
      {rec_block}
      {reasons_block}
    </div>

    {online_html}
    {researcher_html}
    {refs_html}

    <div class="footer">
      <p class="disclaimer">
        هذا التقرير أداة مساعدة آلية؛ القرار التحريري النهائي يعود إلى المجلة.
      </p>
      <p class="service">مُنجز عبر خدمة سبار — sibar.ilmovas.com</p>
    </div>
  </div>
</body>
</html>""".format(
        font_css=font_css,
        body_font_family=body_font_family,
        color=color,
        journal_name=_esc(journal.name),
        report_id=_esc(_report_id_short(check.report_id)),
        date=_fmt_date(check.date_completed),
        article_title=_esc(article.title),
        score=_fmt_score(score),
        verdict_ar=_esc(check.verdict_ar),
        verdict_en=_esc(check.verdict_en),
        rec_block=(
            '<div class="rec-badge">{}</div>'.format(_esc(rec_ar))
            if rec_ar
            else ""
        ),
        reasons_block=(
            '<ul class="reasons">{}</ul>'.format(reasons_html) if reasons_html else ""
        ),
        online_html=online_html,
        researcher_html=researcher_html,
        refs_html=refs_html,
    )

    return HTML(string=html_doc).write_pdf()
