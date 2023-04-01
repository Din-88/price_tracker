import os
from celery import Celery


os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'price_tracker.settings')

import django
django.setup()

app = Celery('scraper')
app.config_from_object('django.conf:settings', namespace='CELERY')

from api_tracker.workers.tasks import *

app.autodiscover_tasks()
