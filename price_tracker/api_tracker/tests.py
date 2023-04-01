import os
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'price_tracker.settings')
import django
django.setup()

from unittest.mock import Mock, patch
from django.test import TestCase
from rest_framework.test import APITestCase
from django.contrib.auth import get_user_model
from rest_framework import status
from dataclasses import dataclass

from api_tracker.models import (
    Tracker,
    TrackersUserSettings,
    NotifyType,
    NotifyCase,
)


class TrackerViewSetTest(APITestCase):
    def setUp(self):
        self.url = 'https://www.sulpak.kz/product/123'
        self.tracker = Tracker.objects.create(
            url=self.url, title='Product 123', price='100.00')
        self.tracker.save()
        pass

    def test_get_detail(self):
        response = self.client.get(f'/api/tracker/{self.tracker.pk}/get/')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        pass

    def test_get_list(self):
        response = self.client.get('/api/tracker/get/')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        pass

    @patch('api_tracker.views.asdict')
    @patch('api_tracker.workers.parsers.parsers.Parsers.get_parser')
    def test_get_update(self, mock_get_parser, mock_asdict):
        mock_asdict.return_value = {'url': self.tracker.url, 'price': 200}

        response = self.client.get(f'/api/tracker/{self.tracker.pk}/update/')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['info']['url'], self.url)
        self.assertEqual(response.data['info']['price'], '200.00')
        self.assertEqual(response.data['info']['prices'][0]['price'], '200.00')

    def test_get_update_unknown_pk(self):
        response = self.client.get('/api/tracker/100500/update/')
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)

    @patch('api_tracker.workers.parsers.parsers.Parsers.get_parser')
    def test_new(self, mock_get_parser):
        @dataclass
        class Info:
            url: str
            price: str

        mock_parser = mock_get_parser.return_value.return_value
        mock_parser.get_info.return_value = Info(price=300, url='new_url')

        response = self.client.post(
            '/api/tracker/new/', data={'url': 'new_url'})
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(response.data['info']['url'], 'new_url')
        self.assertEqual(response.data['info']['price'], '300.00')
        self.assertEqual(response.data['info']['prices'][0]['price'], '300.00')

    @patch('api_tracker.workers.tasks.task_send_mail_admins.apply_async')
    def test_get_new_url_exists(self, mosk_task_send_mail_admins):
        response = self.client.post(
            '/api/tracker/new/', data={'url': self.url})
        self.assertEqual(response.status_code, status.HTTP_302_FOUND)

    def test_get_new_url_unknown(self):
        response = self.client.post(
            '/api/tracker/new/', data={'url': 'url_unknown'})
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(
            response.data['error']['data']['error'], 'url unknown')


class TrackersUserSettingsTest(TestCase):
    def setUp(self):
        self.user = get_user_model().objects.create_user(username='testuser')
        self.notify_case = NotifyCase.objects.get_or_create(case='<>')[0]
        self.notify_type = NotifyType.objects.get_or_create(type='push')[0]

        self.tus = TrackersUserSettings.objects.get(user=self.user)

    def test_creat_trackers_user_settings_for_user(self):
        self.assertTrue(self.tus.user == self.user)
        self.assertTrue(self.tus.notify_case == self.notify_case)
        self.assertTrue(self.tus.notify_types.count() == 1)
        self.assertTrue(self.tus.notify_types.contains(self.notify_type))

    def test_trackers_user_settings_str(self):
        self.assertEqual(str(self.tus), 'testuser')
