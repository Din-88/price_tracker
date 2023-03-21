# import json
# from django.test import TestCase, TransactionTestCase
# from django.test import Client
# from django.urls import reverse

# import django
# django.setup()

# from web.models import Tracker


# class Test_TestTracker(TransactionTestCase):
#     def setUp(self):
#         self.tracker = Tracker(url='url', pk=1)
#         self.tracker.save()
#         pass

#     def test_tracker_update_from_dict(self):
#         d = {'price': 123.00, 'title': 'abcd'}
#         track = Tracker.objects.get(pk=1)
#         track.update_from_dict(dict=d, save=False)
#         self.assertEqual(
#             (track.price, track.title, track.url, track.pk),
#             (123.00, 'abcd', 'url', 1))
#         pass

#     def test_tracker_update_orm(self):
#         d = {'price': 123.00, 'title': 'abcd'}
#         t = Tracker.objects.filter(pk=1).update(**d)
#         track = Tracker.objects.get(pk=1)
#         self.assertEqual(
#             (track.price, track.title, track.url, track.pk),
#             (123.00, 'abcd', 'url', 1))
#         pass


# class Test_TestIndexView(TestCase):
#     @classmethod
#     def setUpTestData(cls):
#         pass

#     def setUp(self):
#         pass

#     def test_index_view(self):
#         response = self.client.get('/')
#         self.assertEqual(response.status_code, 200)

#         response = self.client.post('/')
#         self.assertEqual(response.status_code, 405)
    

# class Test_TestTrackerGetView(TestCase):
#     @classmethod
#     def setUpTestData(cls):
#         pass

#     def setUp(self):
#         self.tracker = Tracker(url='url', pk=1)
#         self.tracker.save()
#         pass

#     def test_tracker_get_view(self):
#         resp = self.client.get(reverse(viewname='tracker_get', args=[1]))
#         self.assertEqual(resp.status_code, 200)
#         self.assertEqual(resp['content-type'], 'application/json')
#         self.assertDictEqual(resp.json(), self.tracker.as_dict())
#         self.assertJSONEqual(resp.json.args[0].content, json.dumps(self.tracker.as_dict()))
#         pass

#     def test_tracker_get_view_not_exist(self):
#         resp = self.client.get(reverse(viewname='tracker_get', args=[0]))
#         self.assertEqual(resp.status_code, 200)
#         self.assertEqual(resp['content-type'], 'application/json')
#         self.assertEqual(resp.json()['error'], 'not exist')


# class Test_TestTrackerCreateView(TestCase):
#     @classmethod
#     def setUpTestData(cls):
#         pass

#     def setUp(self):
#         self.tracker = Tracker(url='url', pk=1)
#         self.tracker.save()
#         self.url = 'https://www.sulpak.kz/g/router_zte__sim_karta_tp_bezlimitishche_mf927u_87_211'
#         pass

#     def test_tracker_create_view_get(self):
#         resp = self.client.get(reverse(viewname='tracker_create'))
#         self.assertEqual(resp.status_code, 400)
    
#     def test_tracker_create_view_post(self):
#         resp = self.client.post(reverse(viewname='tracker_create'))
#         self.assertEqual(resp.status_code, 200)
#         self.assertEqual(resp['content-type'], 'application/json')
#         self.assertContains(resp, 'This field is required.')

#     def test_tracker_create_view_exist(self):
#         url = 'https://www.sulpak.kz/g/router_zte__sim_karta_tp_bezlimitishche_mf927u_87_211'
#         resp = self.client.post(reverse(viewname='tracker_create'), data={'url': url}, follow=True)
#         self.assertEqual(resp.status_code, 200)
#         self.assertEqual(resp['content-type'], 'application/json')

#     def test_tracker_create_view_new(self):
#         url = 'https://www.sulpak.kz/g/karta_pamyati_kingston_microsdxc_32_gb_uhs_i_class_1___a_sdcs232gb_51_202'
#         resp = self.client.post(reverse(viewname='tracker_create'), data={'url': url}, follow=True)
#         self.assertEqual(resp.status_code, 200)
#         self.assertEqual(resp['content-type'], 'application/json')