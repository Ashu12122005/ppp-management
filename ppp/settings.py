"""
Django settings for ppp project.
"""

from pathlib import Path

# -------------------------------------------------
# BASE
# -------------------------------------------------
BASE_DIR = Path(__file__).resolve().parent.parent

# -------------------------------------------------
# SECURITY
# -------------------------------------------------
SECRET_KEY = 'django-insecure-vtp0a^s2@bad%yirxfgnble8%hr+qz$nf_w&inc7k#7mo7m-la'

DEBUG = True

ALLOWED_HOSTS = ["*"]


CSRF_TRUSTED_ORIGINS = [
    "http://127.0.0.1:8000",
    "http://localhost:8000",
]

# -------------------------------------------------
# APPLICATIONS
# -------------------------------------------------
INSTALLED_APPS = [
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',

    # REQUIRED for password reset links
    'django.contrib.sites',

    # Your app
    'core.apps.CoreConfig',
]

SITE_ID = 1

# -------------------------------------------------
# MIDDLEWARE
# -------------------------------------------------
MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    'whitenoise.middleware.WhiteNoiseMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
]


# -------------------------------------------------
# URLS / WSGI
# -------------------------------------------------
ROOT_URLCONF = 'ppp.urls'

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [],   # using app templates
        'APP_DIRS': True,
        'OPTIONS': {
            'context_processors': [
                'django.template.context_processors.request',
                'django.contrib.auth.context_processors.auth',
                'django.contrib.messages.context_processors.messages',
            ],
        },
    },
]

WSGI_APPLICATION = 'ppp.wsgi.application'

# -------------------------------------------------
# DATABASE
# -------------------------------------------------
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': BASE_DIR / 'db.sqlite3',
    }
}

# -------------------------------------------------
# PASSWORD VALIDATION
# -------------------------------------------------
AUTH_PASSWORD_VALIDATORS = [
    {'NAME': 'django.contrib.auth.password_validation.UserAttributeSimilarityValidator'},
    {'NAME': 'django.contrib.auth.password_validation.MinimumLengthValidator'},
    {'NAME': 'django.contrib.auth.password_validation.CommonPasswordValidator'},
    {'NAME': 'django.contrib.auth.password_validation.NumericPasswordValidator'},
]

# -------------------------------------------------
# INTERNATIONALIZATION
# -------------------------------------------------
LANGUAGE_CODE = 'en-us'

TIME_ZONE = 'Asia/Kolkata'

USE_I18N = True
USE_TZ = True

# -------------------------------------------------
# STATIC / MEDIA
# -------------------------------------------------
STATIC_URL = '/static/'
STATICFILES_DIRS = [BASE_DIR / 'core' / 'static']

MEDIA_URL = '/media/'
MEDIA_ROOT = BASE_DIR / 'media'

DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'
STATIC_ROOT = BASE_DIR / 'staticfiles'


# -------------------------------------------------
# AUTH / LOGIN
# -------------------------------------------------
LOGIN_URL = '/login/'
LOGIN_REDIRECT_URL = '/'
LOGOUT_REDIRECT_URL = '/login/'

# -------------------------------------------------
# EMAIL CONFIG (PRODUCTION READY)
# -------------------------------------------------
EMAIL_BACKEND = "django.core.mail.backends.smtp.EmailBackend"

EMAIL_HOST = "smtp.gmail.com"
EMAIL_PORT = 587
EMAIL_USE_TLS = True

EMAIL_HOST_USER = "ashutoshbhanja66@gmail.com"
EMAIL_HOST_PASSWORD = "saufudy zcpzy uxxe".replace(" ", "")  # app password

DEFAULT_FROM_EMAIL = "PPP Management <ashutoshbhanja66@gmail.com>"
