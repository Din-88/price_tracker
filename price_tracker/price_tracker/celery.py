# from __future__ import absolute_import
import os, time
from celery import Celery, shared_task
from django.conf import settings

# settings.configure()
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'price_tracker.settings')

import django
django.setup()

app = Celery('scraper')
app.config_from_object('django.conf:settings', namespace='CELERY')

from api_tracker.workers.tasks import *

app.autodiscover_tasks()