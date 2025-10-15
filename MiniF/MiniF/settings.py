from pathlib import Path
import environ
from datetime import timedelta
import mongoengine
import os

BASE_DIR = Path(__file__).resolve().parent.parent

env = environ.Env(
    DEBUG=(bool, False),
    TIME_ZONE=(str, "Europe/Kyiv"),
    LANGUAGE_CODE=(str, "uk"),
)
environ.Env.read_env(BASE_DIR / ".env")

SECRET_KEY = env("SECRET_KEY")
DEBUG = env("DEBUG")
ALLOWED_HOSTS = [h.strip() for h in env("ALLOWED_HOSTS", default="").split(",") if h.strip()]

INSTALLED_APPS = [
    "django.contrib.admin",
    "django.contrib.auth",
    "django.contrib.contenttypes",
    "django.contrib.sessions",
    "django.contrib.messages",
    "daphne",
    "django.contrib.staticfiles",
    "django.contrib.sites",
    "django_elasticsearch_dsl",
    "django_elasticsearch_dsl_drf",

    "rest_framework",
    "rest_framework.authtoken",
    "allauth",
    "allauth.account",
    "allauth.socialaccount",
    "dj_rest_auth",
    "dj_rest_auth.registration",
    'rest_framework_simplejwt.token_blacklist',
    "rest_framework_simplejwt",
    "reversion",
    "core",
    "users",
    "communications",
    "dashboard",
    "profiles",
    "projects",
    "drf_yasg",
    "notifications",
]

MIDDLEWARE = [
    "django.middleware.security.SecurityMiddleware",
    "django.contrib.sessions.middleware.SessionMiddleware",
    "django.middleware.common.CommonMiddleware",
    "django.middleware.csrf.CsrfViewMiddleware",
    "django.contrib.auth.middleware.AuthenticationMiddleware",
    "django.contrib.messages.middleware.MessageMiddleware",
    "django.middleware.clickjacking.XFrameOptionsMiddleware",
    "allauth.account.middleware.AccountMiddleware",
]

ROOT_URLCONF = "MiniF.urls"

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
            ],
        },
    },
]

WSGI_APPLICATION = "MiniF.wsgi.application"
ASGI_APPLICATION = "MiniF.asgi.application"

if env("DATABASE_URL", default=""):
    DATABASES = {"default": env.db("DATABASE_URL")}
else:
    DATABASES = {
        "default": {
            "ENGINE": "django.db.backends.sqlite3",
            "NAME": BASE_DIR / "db.sqlite3",
        }
    }
CHANNEL_LAYERS = {
    "default": {
        "BACKEND": "channels_redis.core.RedisChannelLayer",
        "CONFIG": {
            "hosts": [("redis", 6379)],
        },
    },
}
mongoengine.connect(host=env("MONGO_URI"))

ELASTICSEARCH_DSL = {

    'default': {

        'hosts': os.getenv('ELASTICSEARCH_URL', 'http://elasticsearch:9200')

    },

}
# Celery settings
CELERY_BROKER_URL = os.environ.get("CELERY_BROKER_URL")
CELERY_RESULT_BACKEND = os.environ.get("CELERY_RESULT_BACKEND")
CELERY_ACCEPT_CONTENT = ["json"]
CELERY_TASK_SERIALIZER = "json"

CELERY_TASK_DEFAULT_RETRY_DELAY = 60
CELERY_TASK_MAX_RETRIES = 3

LANGUAGE_CODE = env("LANGUAGE_CODE")
TIME_ZONE = env("TIME_ZONE")
USE_I18N = True
USE_TZ = True

STATIC_URL = "static/"
STATIC_ROOT = BASE_DIR / "staticfiles"
STATICFILES_DIRS = [BASE_DIR / "static"]

DEFAULT_AUTO_FIELD = "django.db.models.BigAutoField"

REST_FRAMEWORK = {
    "DEFAULT_RENDERER_CLASSES": ["rest_framework.renderers.JSONRenderer"],
    "DEFAULT_PARSER_CLASSES": ["rest_framework.parsers.JSONParser"],
    "DEFAULT_AUTHENTICATION_CLASSES": ("rest_framework_simplejwt.authentication.JWTAuthentication",),
}

AUTH_USER_MODEL = "users.UserProfile"
SITE_ID = 1

REST_AUTH = {
    "REGISTER_SERIALIZER": "users.serializers.UserRegistrationSerializer",
    "PASSWORD_RESET_CONFIRM_SERIALIZER": "users.serializers.CustomPasswordResetConfirmSerializer",
}

AUTH_PASSWORD_VALIDATORS = [
    {"NAME": "django.contrib.auth.password_validation.MinimumLengthValidator", "OPTIONS": {"min_length": 8}},
    {"NAME": "django.contrib.auth.password_validation.CommonPasswordValidator"},
    {"NAME": "django.contrib.auth.password_validation.NumericPasswordValidator"},
    {"NAME": "users.validators.UppercaseValidator"},
]


ACCOUNT_EMAIL_VERIFICATION = "mandatory"
ACCOUNT_SIGNUP_FIELDS = ["email*", "username*", "password1*", "password2*"]
ACCOUNT_LOGIN_METHODS = {"email"}
ACCOUNT_UNIQUE_EMAIL = True
ACCOUNT_CONFIRM_EMAIL_ON_GET = False

EMAIL_BACKEND = "django.core.mail.backends.smtp.EmailBackend"
EMAIL_HOST = "smtp.gmail.com"
EMAIL_PORT = 587
EMAIL_USE_TLS = True
EMAIL_HOST_USER = env("EMAIL_HOST_USER")
EMAIL_HOST_PASSWORD = env("EMAIL_HOST_PASSWORD")
DEFAULT_FROM_EMAIL = env("DEFAULT_FROM_EMAIL")

PASSWORD_RESET_TIMEOUT = 86400 * 7

REST_USE_JWT = True

SIMPLE_JWT = {
    "ACCESS_TOKEN_LIFETIME": timedelta(minutes=10),
    "REFRESH_TOKEN_LIFETIME": timedelta(days=7),
    "AUTH_HEADER_TYPES": ("Bearer",),
}


LOGGING = {
    "version": 1,
    "disable_existing_loggers": False,
    "formatters": {
        "verbose": {
            "format": "{asctime} {levelname} {name} {message}",
            "style": "{",
        },
        "simple": {
            "format": "{levelname} {message}",
            "style": "{",
        },
    },
    "handlers": {
        "console": {
            "level": "DEBUG",
            "class": "logging.StreamHandler",
            "formatter": "simple",
        },
        "file": {
            "level": "WARNING",
            "class": "logging.handlers.TimedRotatingFileHandler",
            "filename": os.path.join(BASE_DIR, "logs/project.log"),
            "when": "midnight",
            "backupCount": 7,
            "formatter": "verbose",
        },
    },
    "loggers": {
        "django": {
            "handlers": ["file"],
            "level": "DEBUG",
            "propagate": True,
        },
        "django.db.backends": {
            "handlers": ["file"],
            "level": "INFO",
            "propagate": False,
        },
        "users": {
            "handlers": ["console", "file"],
            "level": "DEBUG",
            "propagate": True,
        },
        "profiles": {
            "handlers": ["console", "file"],
            "level": "DEBUG",
            "propagate": True,
        },
        "projects": {
            "handlers": ["console", "file"],
            "level": "DEBUG",
            "propagate": True,
        },
        "core": {
            "handlers": ["console", "file"],
            "level": "DEBUG",
            "propagate": True,
        },
        "communications": {
            "handlers": ["console", "file"],
            "level": "DEBUG",
            "propagate": True,
        },
    }
}

SWAGGER_SETTINGS = {
    "SECURITY_DEFINITIONS": {
        "Bearer": {
            "type": "apiKey",
            "in": "header",
            "name": "Authorization",
            "description": "Введи JWT токен у форматі: Bearer <your_token>",
        }
    },
    "USE_SESSION_AUTH": False,
}
