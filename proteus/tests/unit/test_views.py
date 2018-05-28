# coding=utf-8

from django.test import TestCase
from django.urls import reverse
from django.http import HttpResponseNotAllowed


class IndexViewTestCase(TestCase):

    def setUp(self):
        self.response = self.client.get(reverse("index"))

    def test_status_code(self):
        self.assertEquals(self.response.status_code, 200)

    def test_template_used(self):
        self.assertTemplateUsed(self.response, 'index.html')

class ResultViewTestCase(TestCase):
    pass

class ProcessViewTestCase(TestCase):

    def test_request_wrong_method(self):
        response = self.client.post(reverse('process'))
        self.assertEquals(response.status_code, 405)
        self.assertIsInstance(response, HttpResponseNotAllowed)

    def test_right_method(self):
        response = self.client.get(reverse('process'))
        self.assertEquals(response.status_code, 200)