"""
Sibar API client — كشف التكرار وسلامة النشر
Public: https://sibar.ilmovas.com
Docs:   https://sibar.ilmovas.com/docs

Endpoint auth summary:
  Public  (no key): POST /api/v1/check, GET /api/v1/reports/{id}/data,
                    POST /api/v1/verify/dois, GET /api/v1/health
  Protected (X-API-Key header): POST /api/v1/analyze, POST /api/v1/publications,
                                 DELETE /api/v1/publications/{id}
"""
import requests

from utils import setting_handler


class SibarAPIError(Exception):
    pass

# Keep old name as alias so existing imports don't break
SabarAPIError = SibarAPIError


def _get_plugin():
    from utils import models as utils_models
    return utils_models.Plugin.objects.get(name="sabar")


_ALLOWED_HOSTS = {"sibar.ilmovas.com", "api.sibar.ilmovas.com"}


def _validate_url(url):
    from urllib.parse import urlparse
    parsed = urlparse(url)
    if parsed.scheme not in ("https", "http"):
        raise SibarAPIError("Sibar API URL must use http or https.")
    if parsed.hostname not in _ALLOWED_HOSTS:
        raise SibarAPIError(
            "Sibar API URL host '{}' is not allowed. "
            "Permitted hosts: {}".format(parsed.hostname, ", ".join(_ALLOWED_HOSTS))
        )


def _settings(journal):
    plugin = _get_plugin()
    base_url = setting_handler.get_plugin_setting(
        plugin, "sabar_api_url", journal, create=True
    ).value
    api_key = setting_handler.get_plugin_setting(
        plugin, "sabar_api_key", journal, create=True
    ).value
    base_url = (base_url or "https://sibar.ilmovas.com").rstrip("/")
    _validate_url(base_url)
    return base_url, (api_key or "")


def _parse_json_response(resp):
    try:
        return resp.json()
    except ValueError as exc:
        raise SibarAPIError(
            "Sibar API returned HTTP {} with a non-JSON response.".format(resp.status_code)
        ) from exc


def _protected_headers(journal):
    _, api_key = _settings(journal)
    if not api_key:
        raise SibarAPIError(
            "Sibar API key is not configured. "
            "Set it in Manager → Settings → Plugins → Sabar."
        )
    return {"X-API-Key": api_key, "Content-Type": "application/json"}


def health_check(journal):
    """Returns True if Sibar service is reachable."""
    base_url, _ = _settings(journal)
    try:
        resp = requests.get("{}/api/v1/health".format(base_url), timeout=10)
        return resp.ok
    except requests.RequestException:
        return False


def submit_article(article):
    """
    Submit article for duplication detection via POST /api/v1/check.
    This endpoint is PUBLIC — no API key required.

    Returns report_id (str) on success.
    Raises SibarAPIError on failure.
    """
    journal = article.journal
    base_url, _ = _settings(journal)

    dois = []
    try:
        # article's own DOI
        art_doi = article.get_doi()
        if art_doi:
            dois.append(art_doi)
        # any additional doi-type identifiers on the article
        for ident in article.identifier_set.filter(id_type='doi').exclude(identifier=''):
            if ident.identifier and ident.identifier not in dois:
                dois.append(ident.identifier)
    except Exception:
        pass

    orcid = None
    try:
        ca = article.correspondence_author
        if ca and getattr(ca, 'orcid', None):
            orcid = ca.orcid
        if not orcid:
            fa = article.frozenauthor_set.first()
            if fa and getattr(fa, 'orcid', None):
                orcid = fa.orcid
        if not orcid and article.owner and getattr(article.owner, 'orcid', None):
            orcid = article.owner.orcid
    except Exception:
        pass

    payload = {
        "title": article.title or "",
        "abstract": article.abstract or "",
        "journal": journal.name if journal else None,
        "orcid": orcid,
        "dois": dois if dois else None,
    }

    try:
        resp = requests.post(
            "{}/api/v1/check".format(base_url),
            json=payload,
            timeout=60,
        )
    except requests.RequestException as exc:
        raise SibarAPIError("Network error contacting Sibar API: {}".format(exc))

    if not resp.ok:
        raise SibarAPIError(
            "Sibar API returned {}: {}".format(resp.status_code, resp.text[:200].encode("ascii", errors="replace").decode())
        )

    data = _parse_json_response(resp)

    # Use report_id if present, fall back to check id
    report_id = data.get("report_id") or str(data.get("id", ""))
    if not report_id:
        raise SibarAPIError(
            "Sibar API response missing report_id/id: {}".format(data)
        )

    return report_id, data


def fetch_result(journal, report_id):
    """
    Fetch full report data via GET /api/v1/reports/{report_id}/data.
    This endpoint is PUBLIC — no API key required.

    Returns the raw JSON dict from Sibar.
    Raises SibarAPIError on failure.
    """
    base_url, _ = _settings(journal)

    try:
        resp = requests.get(
            "{}/api/v1/reports/{}/data".format(base_url, report_id),
            timeout=30,
        )
    except requests.RequestException as exc:
        raise SibarAPIError("Network error contacting Sibar API: {}".format(exc))

    if resp.status_code == 404:
        raise SibarAPIError("Report not found: {}".format(report_id))

    if not resp.ok:
        raise SibarAPIError(
            "Sibar API returned {}: {}".format(resp.status_code, resp.text[:200].encode("ascii", errors="replace").decode())
        )

    return _parse_json_response(resp)


def run_deep_analysis(journal, article):
    """
    POST /api/v1/analyze — Layer 2 analysis:
    tortured phrases, reference verification, cross-lingual checking.
    PROTECTED — requires X-API-Key.

    Returns raw JSON response.
    """
    base_url, _ = _settings(journal)
    headers = _protected_headers(journal)

    payload = {
        "title": article.title or "",
        "abstract": article.abstract or "",
        "journal": journal.name if journal else None,
    }

    try:
        resp = requests.post(
            "{}/api/v1/analyze".format(base_url),
            json=payload,
            headers=headers,
            timeout=120,
        )
    except requests.RequestException as exc:
        raise SibarAPIError("Network error contacting Sibar API: {}".format(exc))

    if not resp.ok:
        raise SibarAPIError(
            "Sibar analyze returned {}: {}".format(resp.status_code, resp.text[:200].encode("ascii", errors="replace").decode())
        )

    return _parse_json_response(resp)


def verify_dois(journal, dois):
    """
    POST /api/v1/verify/dois — verify a list of DOIs via Crossref.
    PUBLIC — no API key required.

    Returns list of verification results.
    """
    base_url, _ = _settings(journal)

    try:
        resp = requests.post(
            "{}/api/v1/verify/dois".format(base_url),
            json={"dois": dois},
            timeout=30,
        )
    except requests.RequestException as exc:
        raise SibarAPIError("Network error: {}".format(exc))

    if not resp.ok:
        raise SibarAPIError(
            "Sibar verify/dois returned {}: {}".format(resp.status_code, resp.text[:200].encode("ascii", errors="replace").decode())
        )

    return _parse_json_response(resp)
