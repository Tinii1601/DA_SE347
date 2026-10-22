from django.test import TestCase, Client
from django.urls import reverse


class CoreViewsTest(TestCase):
    def setUp(self):
        self.client = Client()

    def test_homepage_loads_status_200(self):
        response = self.client.get(reverse('core:home'), HTTP_HOST='127.0.0.1')
        self.assertEqual(response.status_code, 200)

    def test_contact_page_loads_status_200(self):
        response = self.client.get(reverse('core:contact'), HTTP_HOST='127.0.0.1')
        self.assertEqual(response.status_code, 200)
