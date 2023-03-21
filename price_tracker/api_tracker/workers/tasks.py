from dataclasses import asdict
from django.contrib.auth import get_user_model

from django.conf import settings
from django.db import models
from django.db.models import Count, Subquery, OuterRef
from django.db.models import Value, CharField, Aggregate
from django.db.models.functions import Concat
import time
from random import randint

from django.db.models import Q, F, Sum
from django.utils import timezone
from django.core import mail
from django.core.mail import send_mail
from django.core.mail.backends.smtp import EmailBackend

from celery import shared_task

from webpush import send_user_notification

from ..models import NotifyType, NotifyCase, UserTracker, Tracker, Price
from .parsers.parsers import Parsers
from .utils import GroupConcat, message_updated_trackers


@shared_task()
def task_send_test_mail():
    send_mail(
        subject='test',
        message='test message',
        from_email='testpricetracker@gmail.com',  # settings.EMAIL_HOST_USER,
        recipient_list=['din.vasilevsky@gmail.com'],
        fail_silently = False,
    )


@shared_task
def task_send_test_push(user_pk, msg='Tracker new update'):
    user = get_user_model().objects.get(pk=user_pk)
    payload = {
        "head": f'Hi {user.username}', 
        "body": msg,
        "icon": 'https://i.imgur.com/dRDxiCQ.png',
        "url":  '/',
        # 'badge': 'https://freeiconshop.com/wp-content/uploads/edd/badge-outline-filled.pnghttps://freeiconshop.com/wp-content/uploads/edd/badge-outline-filled.png',
        # 'image': 'https://cdn.pixabay.com/photo/2015/04/23/22/00/tree-736885__480.jpg',
        # 'timestamp': Date.parse('01 Jan 2000 00:00:00'),
    }

    send_user_notification(user=user, payload=payload, ttl=1000)


@shared_task(
    rate_limit=2,
    max_retries=3,
    retry_backoff=5,
    default_retry_delay=5, 
    time_limit=20,
    soft_time_limit=10,
)
def task_send_mail(user_pk, subject, msg, html_message=None):
    recipient = get_user_model().objects \
        .filter(pk=user_pk).only('email').first().email
    send_mail(
        subject=subject,
        message=msg,
        html_message=html_message,
        from_email=settings.EMAIL_HOST_USER,
        recipient_list=[recipient],
        fail_silently = False
    )


@shared_task(
    max_retries=3,
    retry_backoff=5,
    default_retry_delay=5, 
    time_limit=20,
    soft_time_limit=10,
)
def task_send_push(user_pk, msg):
    user = get_user_model().objects.get(pk=user_pk)
    payload = {
        'head': 'Price Tracker',
        # 'title': f'Hi {user.username}',
        'body': msg,
        'icon': '/static/web/favicon/android-chrome-192x192.png',
        'url':  '/profile',
        'requireInteraction': True
        # 'badge': 'https://freeiconshop.com/wp-content/uploads/edd/badge-outline-filled.pnghttps://freeiconshop.com/wp-content/uploads/edd/badge-outline-filled.png',
        # 'image': 'https://cdn.pixabay.com/photo/2015/04/23/22/00/tree-736885__480.jpg',
        # 'timestamp': Date.parse('01 Jan 2000 00:00:00'),
    }

    send_user_notification(user=user, payload=payload, ttl=24*60*60)


@shared_task(
    max_retries=3,
    retry_backoff=5,
    default_retry_delay=5, 
    time_limit=20,
    soft_time_limit=10,
)
def task_set_need_notify(args: tuple[int, None|int|float, None|int|float]):
    '''
    Args:
        - args: tuple[
            - int - tracker_pk,
            - float | int | None - prev_price,
            - float | int | None - curr_price]
    '''
    tracker_pk, prev_price, curr_price = args
    users = get_user_model().objects \
        .filter(trackers__pk=tracker_pk,
                trackers_settings__notify_types__isnull=False) \
        .prefetch_related('trackers_settings').all()

    for user in users:
        if curr_price == prev_price:
            continue

        user_settings = user.trackers_settings        
        user_tracker = user.user_tracker.get(tracker__pk=tracker_pk)

        notify_case = ''
        notify_types = []
        user_notify_case = user_settings.notify_case.case
        user_notify_types = user_settings.notify_types.all()

        if None in [curr_price, prev_price]:
            notify_case = '?-' if curr_price else '-?'
            notify_types = user_notify_types
        else:
            notify_case_map = {
                '<>': '<' if curr_price < prev_price else '>',
                '<' : '<' if curr_price < prev_price else '',
                '>' : '>' if curr_price > prev_price else ''}
            
            notify_type_map = {
                '<>': user_notify_types,
                '<' : user_notify_types if curr_price < prev_price else [],
                '>' : user_notify_types if curr_price > prev_price else []}            
            
            notify_case = notify_case_map.get(user_notify_case, '')
            notify_types = notify_type_map.get(user_notify_case, [])

        user_tracker.need_notify_case = notify_case
        user_tracker.need_notify_types.set(notify_types)
        user_tracker.save()


@shared_task(
    max_retries=3,
    retry_backoff=5,
    default_retry_delay=5, 
    time_limit=20,
    soft_time_limit=10,
)
def task_clear_need_notify(user_tracker_pks, notify_type_pk):
    for obj in UserTracker.objects.filter(pk__in=user_tracker_pks).all():
        obj.need_notify_types.remove(
            NotifyType.objects.get(pk=notify_type_pk)
        )
    pass


@shared_task(
    bind=True,
    max_retries=3,
    retry_backoff=5,
    default_retry_delay=5, 
    time_limit=20,
    soft_time_limit=10,
)
def task_notify_if_need_for_user(self, user_pk):
    user = get_user_model().objects \
        .filter(
            pk=user_pk,
            trackers_settings__notify_types__isnull=False,
            user_tracker__need_notify_types__isnull=False) \
        .only('pk', 'trackers_settings') \
        .first()
    
    if not user:
        return

    user_tracker_pks = user.user_tracker \
        .filter(need_notify_types__isnull=False) \
        .values_list('id', flat=True).all()
    
    user_tracker_pks = list(user_tracker_pks)

    notify_cases = user.user_tracker \
        .filter(need_notify_types__isnull=False) \
        .values('need_notify_case') \
        .annotate(
            # user_trackser_pks=GroupConcat('pk'),
            count=Count('need_notify_case')
        )

    notify_cases = list(notify_cases.all())
    total = sum(map(lambda x:x['count'] , notify_cases))
    msg = message_updated_trackers(notify_cases, total)

    notify_task_ids = user.trackers_settings.notify_task_ids
    notify_task_ids = notify_task_ids.split(',')
    self.app.control.revoke(notify_task_ids)

    task_ids = ''
    for notify_type in user.trackers_settings.notify_types.all():        
        if notify_type.type == 'push':
            task_send = task_send_push.si(user.pk, f'Hi, {user.username}!\r\n'+msg)
        elif notify_type.type == 'mail':
            subject = 'Обновление Трекера'
            task_send = task_send_mail.si(user.pk, subject, msg)                
            
        rt = (task_send | task_clear_need_notify.si(
            user_tracker_pks, notify_type.pk)) \
            .apply_async()
        task_ids += f',{rt.id}'
    
    user.trackers_settings.notify_task_ids = task_ids
    user.trackers_settings.save()


@shared_task(
    max_retries=3,
    retry_backoff=5,
    default_retry_delay=5, 
    time_limit=20,
    soft_time_limit=10,
)
def task_notify_if_need():
    offset, limit = 0, 10
    while True:
        users = get_user_model().objects \
            .filter(
                trackers_settings__notify_types__isnull=False,
                user_tracker__need_notify_types__isnull=False) \
            .only('pk').distinct()[offset: offset+limit]
        if not users:
            break
        for user in users:
            task_notify_if_need_for_user.apply_async(args=(user.pk,))
        offset += limit


@shared_task(
    max_retries=3,
    retry_backoff=5,
    default_retry_delay=5, 
    time_limit=20,
    soft_time_limit=10,
)
def task_parse(tracker_pk):
    tracker = Tracker.objects. \
        only('pk', 'url', 'host', 'price').get(pk=tracker_pk)
    url = tracker.url
    host = tracker.host
    prev_price = tracker.price
    parser = Parsers().get_parser(host=host)
    if parser:
        info = parser(url=url).get_info()
        tracker.update_from_dict(dict=asdict(info))
        tracker.prices.add(Price.objects.create(price=info.price))
        curr_price = info.price
        # tracker.save()
        # return tracker.host
        try:
            prev_price = float(prev_price)
        except:
            prev_price = None
        return tracker_pk, prev_price, curr_price


@shared_task(
    max_retries=3,
    retry_backoff=5,
    default_retry_delay=5, 
    time_limit=20,
    soft_time_limit=10,
)
def task_start_parce_all():
    offset, limit = 0, 10
    hours_ago = timezone.now() - timezone.timedelta(minutes=2)

    while True:
        values = Tracker.objects.order_by('pk') \
            .filter(date_time__lt=hours_ago) \
            .only('pk') \
            .values_list('pk', flat=True)[offset: offset+limit]
        
        if not values:
            break

        for pk in values:
            (task_parse.s(pk) | task_set_need_notify.s()) \
                .apply_async(priority=10)

        offset += limit
