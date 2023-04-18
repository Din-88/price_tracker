from django.test import TestCase
from unittest.mock import patch
from parameterized import parameterized
from celery.result import AsyncResult

from django.contrib.auth import get_user_model

from api_tracker.models import (
    Tracker, Price, NotifyCase, NotifyType,
    TrackersUserSettings,
    UserTracker,
    NotifyType,
)

from .tasks import (
    task_parse,
    task_start_parce_all,
    task_send_mail,
    task_send_test_mail,
    task_send_test_push,
    task_notify_if_need,
    task_set_need_notify,
    task_clear_need_notify,
    task_notify_if_need_for_user,
)

from .utils import message_updated_trackers


class WorkersTests(TestCase):
    def setUp(self):
        self.User = get_user_model()
        self.user_1 = self.User.objects.create(
            username='user_1'
        )
        self.user_2 = self.User.objects.create(
            username='user_2'
        )
        self.tracker_1 = Tracker.objects.create(url='url_1')
        self.tracker_2 = Tracker.objects.create(url='url_2')
        self.tracker_1.save()
        self.user_1.save()

        self.user_1.trackers.add(self.tracker_1)
        self.user_1.trackers.add(self.tracker_2)
        self.user_2.trackers.add(self.tracker_2)

        user_tracker = self.user_1.user_tracker.get(tracker=self.tracker_1)
        user_tracker.notify = True
        user_tracker.need_notify_case = ''
        user_tracker.save()

        user_tracker = self.user_1.user_tracker.get(tracker=self.tracker_2)
        user_tracker.notify = True
        user_tracker.need_notify_case = ''
        user_tracker.need_notify_types \
            .set([NotifyType.objects.get(type='push'),
                  NotifyType.objects.get(type='mail')])
        user_tracker.save()

    def test_task_parse(self):
        result = task_parse.apply(args=[self.tracker_1.pk])
        self.assertTrue(result.successful())

    @patch('api_tracker.workers.tasks.task_parse.s')
    @patch('api_tracker.workers.tasks.task_set_need_notify.s')
    def test_start_parce_all(self,
                             mock_task_set_need_notify,
                             mock_task_parse):
        mock_task_parse.return_value = (1, 2, 3)

        result = task_start_parce_all.apply()
        self.assertTrue(result.successful())

    def test_task_send_test_mail(self):
        result = task_send_test_mail.apply()
        self.assertTrue(result.successful())

    def test_task_send_test_push(self):
        result = task_send_test_push.apply((self.user_1.pk,))
        self.assertTrue(result.successful())

    @parameterized.expand([
        # case, prev, curr, case, type
        ('<>', None, None, '',   False),
        ('<>', None, 1,    '?-', True),
        ('<>', 1,    None, '-?', True),
        ('<>', 1,    1,     '',  False),
        ('<>', 1,    2,    '>',  True),
        ('<>', 2,    1,    '<',  True),
        ('<',  None, None, '',   False),
        ('<',  None, 1,    '?-', True),
        ('<',  1,    None, '-?', True),
        ('<',  1,    1,    '',   False),
        ('<',  1,    2,    '',   False),
        ('<',  2,    1,    '<',  True),
        ('>',  None, None, '',   False),
        ('>',  None, 1,    '?-', True),
        ('>',  1,    None, '-?', True),
        ('>',  1,    1,    '',   False),
        ('>',  1,    2,    '>',  True),
        ('>',  2,    1,    '',   False),
    ])
    def test_task_set_need_notify(
         self, case, prev_price, curr_price, expected_case, expected_types):

        expected_types = NotifyType.objects.filter(type='push') \
            if expected_types else NotifyType.objects.filter(type='empty')

        user_1_settings = TrackersUserSettings.objects \
            .get(pk=self.user_1.trackers_settings.pk)
        user_1_settings.notify_case = NotifyCase.objects.get(case=case)
        user_1_settings.save()

        task_set_need_notify(
            (self.tracker_1.pk, prev_price, curr_price))

        user_tracker = self.user_1.user_tracker.get(tracker=self.tracker_1)

        self.assertEqual(
            user_tracker.need_notify_case, expected_case)

        self.assertQuerysetEqual(
            user_tracker.need_notify_types.all(), expected_types.all(),
            ordered=False)

    @patch('api_tracker.workers.tasks.task_send_push.si')
    @patch('api_tracker.workers.tasks.task_clear_need_notify.si')
    def test_task_notify_if_need_for_user(
         self,
         mock_clear_need_notify,
         mock_task_send_push):

        task_set_need_notify((self.tracker_1.pk, 1, 2))
        task_set_need_notify((self.tracker_2.pk, 2, 1))

        result = task_notify_if_need_for_user \
            .apply(args=(self.user_1.pk,))

        self.assertIsInstance(result, AsyncResult)
        self.assertTrue(result.successful())

        mock_task_send_push.assert_called_with(
            self.user_1.pk,
            'Hi, user_1!\r\n'
            'У Вас 2 обновленныx Трекера.\r\n'
            'Цена на 1 Трекер понизилась.\r\n'
            'Цена на 1 Трекер повысилась.\r\n')

        mock_clear_need_notify.assert_called_with(
            list(self.user_1.user_tracker
                 .filter(tracker__in=[self.tracker_1, self.tracker_2])
                 .values_list('pk', flat=True)),
            NotifyType.objects.get(type='push').pk)

    @patch('api_tracker.workers.tasks.task_notify_if_need_for_user.apply_async')
    def test_task_notify_if_need(
         self,
         mock_task_notify_if_need_for_user):

        result = task_notify_if_need.apply()

        self.assertIsInstance(result, AsyncResult)
        self.assertTrue(result.successful())

        mock_task_notify_if_need_for_user.assert_called_with(
            args=(self.user_1.pk,))

    def test_task_clear_need_send_notify(self):
        notify_type = NotifyType.objects.filter(type='push')
        self.user_1.user_tracker.get(tracker=self.tracker_1) \
            .need_notify_types.set(notify_type)

        task_clear_need_notify(
            [self.user_1.user_tracker.get(tracker=self.tracker_1).pk],
            notify_type.first().pk)
        self.assertQuerysetEqual(
            self.user_1.user_tracker.get(tracker=self.tracker_1)
                .need_notify_types.all(), [])


class WorkersUtilsTests(TestCase):
    def test_generate_message(self):
        notify_cases = [
            {'need_notify_case': '>', 'count': 2},
            {'need_notify_case': '<', 'count': 1}]

        msg = message_updated_trackers(notify_cases, 3)
        expect = 'У Вас 3 обновленныx Трекера.\r\n' \
                 'Цена на 2 Трекера повысилась.\r\n' \
                 'Цена на 1 Трекер понизилась.\r\n'
        self.assertEqual(msg, expect)
