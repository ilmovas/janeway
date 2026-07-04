# SECURITY WARNING: keep the secret key used in production secret!
# You should change this key before you go live!
import os

DEBUG = True
FORCE_BUILTIN_XSL = False
SECRET_KEY = "uxprsdhk^gzd-r=_287byolxn)$k6tsd8_cepl^s^tms2w1qrv"

# This is the default redirect if no other sites are found.
DEFAULT_HOST = "https://www.example.org"
EMAIL_BACKEND = (
    os.environ.get(
        "JANEWAY_EMAIL_BACKEND",
    )
    or "django.core.mail.backends.console.EmailBackend"
)

URL_CONFIG = "path"  # path or domain

MIDDLEWARE = (
    "utils.middleware.TimeMonitoring",
    "debug_toolbar.middleware.DebugToolbarMiddleware",
)
INSTALLED_APPS = [
    "debug_toolbar",
]


BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
PROJECT_DIR = os.path.dirname(BASE_DIR)


def show_toolbar(request):
    return True


DEBUG_TOOLBAR_CONFIG = {
    "SHOW_TOOLBAR_CALLBACK": show_toolbar,
}

HIJACK_LOGIN_REDIRECT_URL = "/manager/"
HIJACK_USERS_ENABLED = True

ENABLE_FULL_TEXT_SEARCH = True

LOGGING = {
    "version": 1,
    "disable_existing_loggers": False,
    "root": {
        "level": "DEBUG",
        "handlers": ["console", "log_file"],
    },
    "formatters": {
        "default": {
            "format": "%(levelname)s %(asctime)s %(module)s "
            "P:%(process)d T:%(thread)d %(message)s",
        },
        "coloured": {
            "()": "colorlog.ColoredFormatter",
            "format": "%(log_color)s%(levelname)s %(asctime)s %(module)s "
            "P:%(process)d T:%(thread)d %(message)s",
            "log_colors": {
                "DEBUG": "green",
                "WARNING": "yellow",
                "ERROR": "red",
                "CRITICAL": "red",
            },
        },
    },
    "handlers": {
        "console": {
            "level": "DEBUG",
            "class": "logging.StreamHandler",
            "formatter": "coloured",
            "stream": "ext://sys.stdout",
        },
        "log_file": {
            "level": "DEBUG",
            "class": "logging.handlers.RotatingFileHandler",
            "maxBytes": 1024 * 1024 * 50,  # 50 MB
            "backupCount": 1,
            "filename": os.path.join(PROJECT_DIR, "logs/janeway.log"),
            "formatter": "default",
        },
    },
    "loggers": {
        "django.db.backends": {
            #'level': 'DEBUG',
            "level": "WARNING",
            "handlers": ["console", "log_file"],
            "propagate": False,
        },
    },
}

# ── Ilmovas: إعداد الوصول خلف ratq-proxy (HTTPS) ──
CSRF_TRUSTED_ORIGINS = ["https://journals.ilmovas.com"]
SECURE_PROXY_SSL_HEADER = ("HTTP_X_FORWARDED_PROTO", "https")
USE_X_FORWARDED_HOST = True

# ── Ilmovas: production-safe static serving (removes :8000, enables DEBUG=False) ──
DEBUG = False

# Prevent middleware merge — full list replaces global (WhiteNoise after SecurityMiddleware)
MERGEABLE_SETTINGS = {"INSTALLED_APPS"}

# Insert WhiteNoise middleware right after Django's SecurityMiddleware.
# We use a thin subclass (defined below) so WhiteNoise serves BOTH the
# collected static files AND the user-uploaded MEDIA_ROOT under /media/.
import core.janeway_global_settings as _g
_WHITENOISE_MW = "core.dev_settings.WhiteNoiseMediaMiddleware"
_mw = list(_g.MIDDLEWARE)
if _WHITENOISE_MW not in _mw:
    _idx = _mw.index("django.middleware.security.SecurityMiddleware") + 1
    _mw.insert(_idx, _WHITENOISE_MW)
MIDDLEWARE = tuple(_mw)

# WhiteNoise compressed static storage
STORAGES = {
    "default": {"BACKEND": "django.core.files.storage.FileSystemStorage"},
    "staticfiles": {"BACKEND": "whitenoise.storage.CompressedStaticFilesStorage"},
}

# ── Ilmovas: serve /media/ user-uploaded files via WhiteNoise (DEBUG=False) ──
# After DEBUG=False, Django no longer serves MEDIA_ROOT, so /media/ requests
# fell through to the site router and returned a 302 redirect instead of the
# file. WhiteNoise only serves STATIC_ROOT@STATIC_URL out of the box, so we
# subclass its middleware and register MEDIA_ROOT@MEDIA_URL as an extra root.
#
# AUTOREFRESH is required because media files are uploaded *after* the worker
# starts; without it WhiteNoise would only index files present at boot.
WHITENOISE_AUTOREFRESH = True

from django.conf import settings as _django_settings
from whitenoise.middleware import WhiteNoiseMiddleware as _WhiteNoiseMiddleware


class WhiteNoiseMediaMiddleware(_WhiteNoiseMiddleware):
    """WhiteNoise that also serves MEDIA_ROOT under MEDIA_URL (/media/)."""

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        media_root = getattr(_django_settings, "MEDIA_ROOT", None)
        media_url = getattr(_django_settings, "MEDIA_URL", None)
        if media_root and media_url and os.path.isdir(media_root):
            self.add_files(media_root, prefix=media_url)


# ── Ilmovas: lock to Arabic + English only (override Janeway's 7-language list) ──
from django.utils.translation import gettext_lazy as _ilmovas_gettext
LANGUAGES = (
    ("en", _ilmovas_gettext("English")),
    ("ar", _ilmovas_gettext("العربية")),
)
LANGUAGE_CODE = "en"
# Philosophy A: the UI switcher (LANGUAGES) is en+ar only, but modeltranslation must
# keep the inherited legacy codes registered so their columns stay DORMANT in the DB
# (never dropped). We only ADD Arabic. No UI path writes to the legacy columns.
MODELTRANSLATION_LANGUAGES = ("en", "ar", "en-us", "fr", "de", "nl", "cy", "es")
MODELTRANSLATION_DEFAULT_LANGUAGE = "en"
