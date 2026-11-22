"""Тести маршрутів додатка pages. Запуск: python manage.py test pages"""

from django.test import TestCase
from django.urls import reverse


class PagesTests(TestCase):
    def test_index(self):
        response = self.client.get(reverse("index"))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "<h1>Вітаємо на сайті mysite!</h1>", html=True)

    def test_about(self):
        response = self.client.get(reverse("about"))
        self.assertContains(response, "Практична робота:")

    def test_contact_without_name(self):
        response = self.client.get(reverse("contact"))
        self.assertContains(response, "<h1>Контакти</h1>", html=True)

    def test_contact_with_name_is_escaped(self):
        response = self.client.get(reverse("contact"), {"name": "<b>Олена</b>"})
        self.assertContains(response, "Вітаю, &lt;b&gt;Олена&lt;/b&gt;!")
