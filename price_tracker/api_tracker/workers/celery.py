import os
from celery import Celery
from django.conf import settings

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'price_tracker.settings')

import django
django.setup()

app = Celery('price_tracker')
app.config_from_object('django.conf:settings', namespace='CELERY')

from api_tracker.workers.tasks import *

app.autodiscover_tasks()
