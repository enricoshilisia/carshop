"""
Django settings — Vehicle-Fitment Parts Store.

Designed for cPanel shared hosting (Passenger + MySQL) but runs anywhere.
All environment-specific values come from .env via python-decouple.
"""
from pathlib import Path

from decouple import Csv, config

BASE_DIR = Path(__file__).resolve().parent.parent

SECRET_KEY = config("SECRET_KEY", default="dev-only-insecure-key-change-me")
DEBUG = config("DEBUG", default=True, cast=bool)
ALLOWED_HOSTS = config("ALLOWED_HOSTS", default="localhost,127.0.0.1", cast=Csv())

INSTALLED_APPS = [
    "django.contrib.admin",
    "django.contrib.auth",
    "django.contrib.contenttypes",
    "django.contrib.sessions",
    "django.contrib.messages",
    "django.contrib.staticfiles",
    # third party
    "rest_framework",
    "treebeard",
    # project
    "apps.core",
    "apps.vehicles",
    "apps.catalog",
    "apps.fitment",
    "apps.jobs",
    "apps.seo",
    "apps.api",
]

MIDDLEWARE = [
    "django.middleware.security.SecurityMiddleware",
    "whitenoise.middleware.WhiteNoiseMiddleware",
    "django.contrib.sessions.middleware.SessionMiddleware",
    "django.middleware.common.CommonMiddleware",
    "django.middleware.csrf.CsrfViewMiddleware",
    "django.contrib.auth.middleware.AuthenticationMiddleware",
    "django.contrib.messages.middleware.MessageMiddleware",
    "django.middleware.clickjacking.XFrameOptionsMiddleware",
    "apps.core.middleware.ApiCorsMiddleware",
]

# Browser-facing API consumers (vehicle selector, search). "*" is fine for a
# public read-only catalog; tighten to SITE_BASE_URL if you add authed endpoints.
CORS_ALLOW_ORIGIN = config("CORS_ALLOW_ORIGIN", default="*")

ROOT_URLCONF = "config.urls"

TEMPLATES = [
    {
        "BACKEND": "django.template.backends.django.DjangoTemplates",
        "DIRS": [],
        "APP_DIRS": True,
        "OPTIONS": {
            "context_processors": [
                "django.template.context_processors.request",
                "django.contrib.auth.context_processors.auth",
                "django.contrib.messages.context_processors.messages",
            ],
        },
    },
]

WSGI_APPLICATION = "config.wsgi.application"

# MySQL 8 / MariaDB 10.6+ in production; SQLite for local development.
DB_ENGINE = config("DB_ENGINE", default="sqlite")
if DB_ENGINE == "mysql":
    DATABASES = {
        "default": {
            "ENGINE": "django.db.backends.mysql",
            "NAME": config("DB_NAME"),
            "USER": config("DB_USER"),
            "PASSWORD": config("DB_PASSWORD"),
            "HOST": config("DB_HOST", default="localhost"),
            "PORT": config("DB_PORT", default="3306"),
            "OPTIONS": {"charset": "utf8mb4"},
        }
    }
else:
    DATABASES = {
        "default": {
            "ENGINE": "django.db.backends.sqlite3",
            "NAME": BASE_DIR / "db.sqlite3",
        }
    }

# Shared hosting: no Redis. Database cache table (manage.py createcachetable).
CACHES = {
    "default": {
        "BACKEND": "django.core.cache.backends.db.DatabaseCache",
        "LOCATION": "django_cache",
        "TIMEOUT": 3600,
        "OPTIONS": {"MAX_ENTRIES": 20000, "CULL_FREQUENCY": 4},
    }
}
SESSION_ENGINE = "django.contrib.sessions.backends.cached_db"

AUTH_PASSWORD_VALIDATORS = [
    {"NAME": "django.contrib.auth.password_validation.UserAttributeSimilarityValidator"},
    {"NAME": "django.contrib.auth.password_validation.MinimumLengthValidator"},
    {"NAME": "django.contrib.auth.password_validation.CommonPasswordValidator"},
    {"NAME": "django.contrib.auth.password_validation.NumericPasswordValidator"},
]

LANGUAGE_CODE = "en"
TIME_ZONE = "Africa/Nairobi"
USE_I18N = True
USE_TZ = True

STATIC_URL = "/static/"
STATIC_ROOT = BASE_DIR / "staticfiles"
STORAGES = {
    "default": {"BACKEND": "django.core.files.storage.FileSystemStorage"},
    "staticfiles": {"BACKEND": "whitenoise.storage.CompressedManifestStaticFilesStorage"},
}

MEDIA_URL = "/media/"
MEDIA_ROOT = BASE_DIR / "media"

# Static XML sitemaps / feeds written by cron, served by WhiteNoise/Cloudflare.
SITEMAP_DIR = Path(config("SITEMAP_DIR", default=str(BASE_DIR / "static" / "sitemaps")))
FEED_DIR = Path(config("FEED_DIR", default=str(BASE_DIR / "static" / "feeds")))
STATICFILES_DIRS = [BASE_DIR / "static"]

DEFAULT_AUTO_FIELD = "django.db.models.BigAutoField"

REST_FRAMEWORK = {
    "DEFAULT_RENDERER_CLASSES": ["rest_framework.renderers.JSONRenderer"],
    "DEFAULT_PERMISSION_CLASSES": ["rest_framework.permissions.AllowAny"],
    "UNAUTHENTICATED_USER": None,
}

# Storefront / edge integration
SITE_BASE_URL = config("SITE_BASE_URL", default="http://localhost:3000")
API_BASE_URL = config("API_BASE_URL", default="http://localhost:8000")
REVALIDATE_SECRET = config("REVALIDATE_SECRET", default="dev-revalidate-secret")
CLOUDFLARE_ZONE_ID = config("CLOUDFLARE_ZONE_ID", default="")
CLOUDFLARE_API_TOKEN = config("CLOUDFLARE_API_TOKEN", default="")

# SEO rule thresholds (Phase 3 rule engine)
SEO_MIN_PRODUCTS_STOREFRONT = 10
SEO_MIN_PRODUCTS_VEHICLE_CATEGORY = 5
SITEMAP_SHARD_SIZE = 45000

if not DEBUG:
    CSRF_TRUSTED_ORIGINS = config("CSRF_TRUSTED_ORIGINS", default="", cast=Csv())
    SECURE_PROXY_SSL_HEADER = ("HTTP_X_FORWARDED_PROTO", "https")
