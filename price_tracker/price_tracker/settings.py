import os
from pathlib import Path

DEBUG = False


BASE_DIR = Path(__file__).resolve().parent.parent

SECRET_KEY = os.environ.get('SECRET_KEY')

ALLOWED_HOSTS = os.environ.get('ALLOWED_HOSTS').split(' ')
CSRF_TRUSTED_ORIGINS=['https://price-tracker.ddns.net']

APPEND_SLASH = True

SITE_ID = 2


INSTALLED_APPS = [
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'django.contrib.sites',

    'django_celery_beat',

    'allauth',
    'allauth.account',    
    'allauth.socialaccount',
    'allauth.socialaccount.providers.google',

    'rest_framework',
    'rest_framework.authtoken',

    'dj_rest_auth',
    'dj_rest_auth.registration',

    'drf_yasg',
    'webpush',

    'web',
    'api_profile',
    'api_tracker',
]

AUTH_USER_MODEL = 'api_profile.User'


REST_FRAMEWORK = {
    'DEFAULT_AUTHENTICATION_CLASSES': [
        # 'rest_framework.authentication.BasicAuthentication',
        'rest_framework.authentication.SessionAuthentication',
        # 'rest_framework.authentication.TokenAuthentication',s
    ],
    'DEFAULT_PERMISSION_CLASSES': [
        'rest_framework.permissions.IsAuthenticated',
    ],
    'EXCEPTION_HANDLER': 'api_tracker.utils.exception_handler',
}

SOCIALACCOUNT_LOGIN_ON_GET=True

AUTHENTICATION_BACKENDS = [
    'django.contrib.auth.backends.ModelBackend',
    'allauth.account.auth_backends.AuthenticationBackend'
]

ACCOUNT_UNIQUE_EMAIL = True
ACCOUNT_EMAIL_REQUIRED = True
ACCOUNT_USERNAME_REQUIRED = False
ACCOUNT_AUTHENTICATION_METHOD = 'email'
ACCOUNT_LOGOUT_REDIRECT_URL = '/'
ACCOUNT_SIGNUP_REDIRECT_URL = '/profile/'
LOGIN_REDIRECT_URL = '/profile/'


SOCIALACCOUNT_AUTO_SIGNUP = True
SOCIALACCOUNT_LOGIN_ON_GET = True
SOCIALACCOUNT_EMAIL_REQUIRED = True
SOCIALACCOUNT_GOOGLE_CALLBACK = os.environ.get('SOCIALACCOUNT_GOOGLE_CALLBACK')

SOCIALACCOUNT_ADAPTER = 'web.adapter.SocialAccountAdapter'

SOCIALACCOUNT_PROVIDERS = {
    'google': {
        'APP': {
            'client_id': os.environ.get('SOCIALACCOUNT_CLIENT_ID'),
            'secret': os.environ.get('SOCIALACCOUNT_SECRET'),
            'key': ''
        },
        'SCOPE': [
            'email',
            'openid',
            'profile',
        ],
        'AUTH_PARAMS': {
            'access_type': 'offline',
        }
    }
}

REST_SESSION_LOGIN = True
REST_USE_JWT = False

# SWAGGER_SETTINGS = {
#     'LOGIN_URL': 'api/login/',
#     'LOGOUT_URL': 'api/logout/',
# }

# # For demo purposes only. Use a white list in the real world.
# CORS_ORIGIN_ALLOW_ALL = True

DEFAULT_AUTO_FIELD = 'django.db.models.AutoField'


MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.locale.LocaleMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
]

ROOT_URLCONF = 'price_tracker.urls'

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [
            os.path.join(BASE_DIR, 'templates'),
            os.path.join(BASE_DIR, 'web/templates')
        ],
        'APP_DIRS': True,
        'OPTIONS': {
            'context_processors': [
                'django.template.context_processors.debug',
                'django.template.context_processors.request',
                'django.contrib.auth.context_processors.auth',
                'django.contrib.messages.context_processors.messages',
            ],
        },
    },
]

WSGI_APPLICATION = 'price_tracker.wsgi.application'


DATABASES = {
    "default": {
        "ENGINE": "django.db.backends.postgresql",
        "NAME": os.environ.get('POSTGRES_DB'),
        "USER": os.environ.get('POSTGRES_USER'),
        "PASSWORD": os.environ.get('POSTGRES_PASSWORD'),
        "HOST": os.environ.get('POSTGRES_HOST'),
        "PORT": os.environ.get('POSTGRES_PORT'),
    }
}


AUTH_PASSWORD_VALIDATORS = [
    {
        'NAME': 'django.contrib.auth.password_validation.UserAttributeSimilarityValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.MinimumLengthValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.CommonPasswordValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.NumericPasswordValidator',
    },
]


# Internationalization
USE_TZ = True
USE_I18N = True
TIME_ZONE = 'UTC'
LANGUAGE_CODE = 'ru-ru'
LOCALE_PATHS = ['locale/',]


STATIC_URL = 'static/'
STATIC_ROOT = os.path.join(BASE_DIR, 'static')


DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'


# Celery settings
r = os.environ.get("REDIS_HOST")
CELERY_BEAT_SCHEDULER='django_celery_beat.schedulers:DatabaseScheduler'
CELERY_BROKER_URL = f'redis://{os.environ.get("REDIS_HOST")}:{os.environ.get("REDIS_PORT")}'
CELERY_RESULT_BACKEND = f'redis://{os.environ.get("REDIS_HOST")}:{os.environ.get("REDIS_PORT")}'

CELERY_BROKER_URL = "redis://redis:6379"
CELERY_RESULT_BACKEND = "redis://redis:6379/0"
CELERYD_LOG_FILE=f'{BASE_DIR}/logs/celery/%n%I.log'


EMAIL_BACKEND = 'django.core.mail.backends.smtp.EmailBackend'
EMAIL_PORT = 587
EMAIL_USE_TLS = True
EMAIL_HOST = 'smtp.gmail.com'
EMAIL_HOST_USER = os.environ.get('EMAIL_HOST_USER')
EMAIL_HOST_PASSWORD = os.environ.get('EMAIL_HOST_PASSWORD')
EMAIL_SENDER_EMAIL = os.environ.get('EMAIL_SENDER_EMAIL')


WEBPUSH_SETTINGS = {
    'VAPID_PUBLIC_KEY': os.environ.get('VAPID_PUBLIC_KEY'),
    'VAPID_PRIVATE_KEY': os.environ.get('VAPID_PRIVATE_KEY'),
    'VAPID_ADMIN_EMAIL': os.environ.get('VAPID_ADMIN_EMAIL')
}

env = os.environ.get('ENVIRONMENT')

if os.environ.get('ENVIRONMENT') == 'dev':
    from .settings_dev import *