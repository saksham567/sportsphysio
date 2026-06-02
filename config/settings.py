"""
Django settings for Dr. Aahana Gupta Sports Physiotherapy platform.
"""
from pathlib import Path

import environ

BASE_DIR = Path(__file__).resolve().parent.parent

env = environ.Env(
    DEBUG=(bool, True),
    ALLOWED_HOSTS=(list, ["localhost", "127.0.0.1"]),
    SECRET_KEY=(str, "django-insecure-change-me-in-production"),
)

environ.Env.read_env(BASE_DIR / ".env")

SECRET_KEY = env("SECRET_KEY")
DEBUG = env("DEBUG")
ALLOWED_HOSTS = env("ALLOWED_HOSTS")

INSTALLED_APPS = [
    "django.contrib.admin",
    "django.contrib.auth",
    "django.contrib.contenttypes",
    "django.contrib.sessions",
    "django.contrib.messages",
    "django.contrib.staticfiles",
    "accounts",
    "website",
    "portal",
    "staff",
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
]

ROOT_URLCONF = "config.urls"

TEMPLATES = [
    {
        "BACKEND": "django.template.backends.django.DjangoTemplates",
        "DIRS": [BASE_DIR / "templates"],
        "APP_DIRS": True,
        "OPTIONS": {
            "context_processors": [
                "django.template.context_processors.debug",
                "django.template.context_processors.request",
                "django.contrib.auth.context_processors.auth",
                "django.contrib.messages.context_processors.messages",
                "website.context_processors.site_settings",
            ],
        },
    },
]

WSGI_APPLICATION = "config.wsgi.application"

DATABASES = {
    "default": env.db(
        "DATABASE_URL",
        default=f"sqlite:///{BASE_DIR / 'db.sqlite3'}",
    )
}
# Render PostgreSQL — keep connections warm across requests
if DATABASES["default"]["ENGINE"].endswith("postgresql"):
    DATABASES["default"].setdefault("CONN_MAX_AGE", 600)

AUTH_PASSWORD_VALIDATORS = [
    {"NAME": "django.contrib.auth.password_validation.UserAttributeSimilarityValidator"},
    {"NAME": "django.contrib.auth.password_validation.MinimumLengthValidator"},
    {"NAME": "django.contrib.auth.password_validation.CommonPasswordValidator"},
    {"NAME": "django.contrib.auth.password_validation.NumericPasswordValidator"},
]

AUTH_USER_MODEL = "accounts.User"

LANGUAGE_CODE = "en-in"
TIME_ZONE = "Asia/Kolkata"
USE_I18N = True
USE_TZ = True

STATIC_URL = "/static/"
STATIC_ROOT = BASE_DIR / "staticfiles"
STATICFILES_DIRS = [BASE_DIR / "static"]
# Use non-manifest storage — avoids 500s when collectstatic runs at a different DEBUG than runtime
STORAGES = {
    "default": {
        "BACKEND": "django.core.files.storage.FileSystemStorage",
    },
    "staticfiles": {
        "BACKEND": (
            "whitenoise.storage.CompressedStaticFilesStorage"
            if not DEBUG
            else "django.contrib.staticfiles.storage.StaticFilesStorage"
        ),
    },
}

MEDIA_URL = "/media/"
MEDIA_ROOT = BASE_DIR / "media"

DEFAULT_AUTO_FIELD = "django.db.models.BigAutoField"

LOGIN_URL = "accounts:login"
LOGIN_REDIRECT_URL = "portal:dashboard"
LOGOUT_REDIRECT_URL = "website:home"

# Practice-specific settings (override via .env in production)
UPI_ID = env("UPI_ID", default="aahanagupta1791@oksbi")
CALENDLY_URL = env(
    "CALENDLY_URL",
    default="https://calendly.com/shoyokageyamaa640?hide_gdpr_banner=1&primary_color=185FA5",
)
CALENDLY_REHAB_URL = env(
    "CALENDLY_REHAB_URL",
    default="https://calendly.com/shoyokageyamaa640?hide_gdpr_banner=1&primary_color=0F6E56",
)
CONTACT_EMAIL = env("CONTACT_EMAIL", default="aahanaguptaphysio@gmail.com")
INSTAGRAM_HANDLE = env("INSTAGRAM_HANDLE", default="@sportsphysiolifts")
INSTAGRAM_URL = env("INSTAGRAM_URL", default="https://instagram.com/sportsphysiolifts")

SITE_URL = env("SITE_URL", default="http://127.0.0.1:8000")

# Email (console in dev; set SMTP vars in production)
EMAIL_BACKEND = env(
    "EMAIL_BACKEND",
    default="django.core.mail.backends.console.EmailBackend",
)
EMAIL_HOST = env("EMAIL_HOST", default="")
EMAIL_PORT = env.int("EMAIL_PORT", default=587)
EMAIL_HOST_USER = env("EMAIL_HOST_USER", default="")
EMAIL_HOST_PASSWORD = env("EMAIL_HOST_PASSWORD", default="")
EMAIL_USE_TLS = env.bool("EMAIL_USE_TLS", default=True)
DEFAULT_FROM_EMAIL = env("DEFAULT_FROM_EMAIL", default=CONTACT_EMAIL)

# Calendly webhook
CALENDLY_WEBHOOK_SIGNING_KEY = env("CALENDLY_WEBHOOK_SIGNING_KEY", default="")

# Razorpay
RAZORPAY_KEY_ID = env("RAZORPAY_KEY_ID", default="")
RAZORPAY_KEY_SECRET = env("RAZORPAY_KEY_SECRET", default="")
RAZORPAY_WEBHOOK_SECRET = env("RAZORPAY_WEBHOOK_SECRET", default="")

# WhatsApp click-to-chat number (country code, no +) e.g. 919876543210
WHATSAPP_NUMBER = env("WHATSAPP_NUMBER", default="919675191210")
WHATSAPP_PREFILL_MESSAGE = env(
    "WHATSAPP_PREFILL_MESSAGE",
    default="Hi Dr. Aahana, I'd like to know more about your physiotherapy services.",
)

# WhatsApp via Twilio (automated messages to patients)
TWILIO_ACCOUNT_SID = env("TWILIO_ACCOUNT_SID", default="")
TWILIO_AUTH_TOKEN = env("TWILIO_AUTH_TOKEN", default="")
TWILIO_WHATSAPP_FROM = env("TWILIO_WHATSAPP_FROM", default="")

if not DEBUG:
    SECURE_BROWSER_XSS_FILTER = True
    SECURE_CONTENT_TYPE_NOSNIFF = True
    SESSION_COOKIE_SECURE = True
    CSRF_COOKIE_SECURE = True
    SECURE_SSL_REDIRECT = env.bool("SECURE_SSL_REDIRECT", default=True)
    SECURE_PROXY_SSL_HEADER = ("HTTP_X_FORWARDED_PROTO", "https")
    CSRF_TRUSTED_ORIGINS = env.list("CSRF_TRUSTED_ORIGINS", default=[])
    if not CSRF_TRUSTED_ORIGINS and SITE_URL.startswith("https://"):
        CSRF_TRUSTED_ORIGINS = [SITE_URL.rstrip("/")]
