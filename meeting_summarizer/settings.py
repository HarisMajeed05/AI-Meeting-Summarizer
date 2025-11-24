import os
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent.parent

SECRET_KEY = "replace-with-a-secure-secret-key"

DEBUG = True

ALLOWED_HOSTS = []

INSTALLED_APPS = [
    "django.contrib.admin",
    "django.contrib.auth",
    "django.contrib.contenttypes",
    "django.contrib.sessions",
    "django.contrib.messages",
    "django.contrib.staticfiles",
    "webapp",
]

MIDDLEWARE = [
    "django.middleware.security.SecurityMiddleware",
    "django.contrib.sessions.middleware.SessionMiddleware",
    "django.middleware.common.CommonMiddleware",
    "django.middleware.csrf.CsrfViewMiddleware",
    "django.contrib.auth.middleware.AuthenticationMiddleware",
    "django.contrib.messages.middleware.MessageMiddleware",
    "django.middleware.clickjacking.XFrameOptionsMiddleware",
]

ROOT_URLCONF = "meeting_summarizer.urls"

TEMPLATES = [
    {
        "BACKEND": "django.template.backends.django.DjangoTemplates",
        "DIRS": [BASE_DIR / "webapp" / "templates"],
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

WSGI_APPLICATION = "meeting_summarizer.wsgi.application"
ASGI_APPLICATION = "meeting_summarizer.asgi.application"

DATABASES = {
    "default": {
        "ENGINE": "django.db.backends.sqlite3",
        "NAME": BASE_DIR / "db.sqlite3",
    }
}

AUTH_PASSWORD_VALIDATORS = []  # simplified for project

LANGUAGE_CODE = "en-us"
TIME_ZONE = "UTC"
USE_I18N = True
USE_TZ = True

STATIC_URL = "/static/"
STATIC_ROOT = BASE_DIR / "staticfiles"
STATICFILES_DIRS = []

MEDIA_URL = "/media/"
MEDIA_ROOT = BASE_DIR / "media"

DEFAULT_AUTO_FIELD = "django.db.models.BigAutoField"

# === ARCHITECTURE-RELATED CONFIG (Infra / Config Layer) ===

# NLP & ASR model names
ASR_MODEL_NAME = "openai/whisper-small"           # ASR Service (Whisper)
SUMMARIZER_MODEL_NAME = "facebook/bart-large-cnn"  # BART summarizer

# Date parsing preferences
DATE_ORDER = "MDY"  # change to "DMY" for day-first dates

# Summariser / chunker constraints
SUMMARIZER_MAX_LEN = 150
SUMMARIZER_MIN_LEN = 1
CHUNK_MAX_CHARS = 1200
TOKENIZER_MODEL_MAX_LENGTH = 1024

# Application/business constraints
MAX_TEXT_LENGTH = 20000  # characters
MAX_AUDIO_FILE_SIZE_MB = 25

# HF Inference API (optional model serving)
HF_API_KEY = os.getenv("HF_API_KEY", "")

# Simple logging configuration hook (can be expanded)
LOGGING = {
    "version": 1,
    "disable_existing_loggers": False,
    "handlers": {
        "console": {"class": "logging.StreamHandler"},
    },
    "root": {
        "handlers": ["console"],
        "level": "INFO",
    },
}
