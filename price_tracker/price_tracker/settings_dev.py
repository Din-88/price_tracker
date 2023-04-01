# settings_dev.py

import os
from pathlib import Path
import platform


DEBUG = True

BASE_DIR = Path(__file__).resolve().parent.parent

CSRF_TRUSTED_ORIGINS = ['http://localhost:8000']
ALLOWED_HOSTS = '*'.split(' ')

TEST_RUNNER = [
    'django.test.runner.DiscoverRunner',
    'djcelery.contrib.test_runner.CeleryTestSuiteRunner',
]

SITE_ID = 1

# ACCOUNT_AUTHENTICATION_METHOD (="username" | "email" | "username_email")
# ACCOUNT_EMAIL_VERIFICATION = 'mandatory'

SOCIALACCOUNT_GOOGLE_CALLBACK = 'http://localhost:8000/google/callback/'


# DATABASES = {
#     'default': {
#         'ENGINE': 'django.db.backends.sqlite3',
#         'NAME': BASE_DIR / 'db.sqlite3',
#     },
#     'OPTIONS': {
#         'timeout': 60,
#     }
# }


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

if platform.system() == 'Windows':
    DATABASES = {
        'default': {
            'ENGINE': 'django.db.backends.sqlite3',
            'NAME': BASE_DIR / 'db.sqlite3',
        },
        'OPTIONS': {
            'timeout': 60,
        }
    }


# SWAGGER_SETTINGS = {
#     'LOGIN_URL': 'api/login/',
#     'LOGOUT_URL': 'api/logout/',
# }

# # For demo purposes only. Use a white list in the real world.
# CORS_ORIGIN_ALLOW_ALL = True

# EMAIL_BACKEND = 'django.core.mail.backends.console.EmailBackend'


# CELERY_TASK_ALWAYS_EAGER = True
