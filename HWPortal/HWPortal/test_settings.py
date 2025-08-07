# test_settings.py
from .settings import *

# Pro testy použití SQLite v paměti
DATABASES = {
    "default": {
        "ENGINE": "django.db.backends.sqlite3",
        "NAME": ":memory:",
    }
}

# Zrychli testy
PASSWORD_HASHERS = [
    "django.contrib.auth.hashers.MD5PasswordHasher",
]

# Vypni migrace cache pro testy
MIGRATION_MODULES = {
    "viewer": None,
}

# Debug pro testy
DEBUG = True

# Zjednodušené logování pro testy
LOGGING = {
    "version": 1,
    "disable_existing_loggers": False,
    "handlers": {
        "console": {
            "class": "logging.StreamHandler",
        },
    },
    "root": {
        "handlers": ["console"],
        "level": "WARNING",
    },
}

# Vypni některé middleware pro rychlejší testy
MIDDLEWARE = [
    "django.middleware.security.SecurityMiddleware",
    "django.contrib.sessions.middleware.SessionMiddleware",
    "django.middleware.common.CommonMiddleware",
    "django.middleware.csrf.CsrfViewMiddleware",
    "django.contrib.auth.middleware.AuthenticationMiddleware",
    "django.contrib.messages.middleware.MessageMiddleware",
]

# Pro Selenium testy
STATICFILES_STORAGE = "django.contrib.staticfiles.storage.StaticFilesStorage"
