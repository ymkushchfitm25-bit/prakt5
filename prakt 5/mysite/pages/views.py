"""Views додатка pages."""

from django.http import HttpResponse
from django.urls import reverse
from django.utils.html import escape

COURSE = "Програмування на Python: веб-фреймворки"
PRACTICE_NUMBER = 5
STUDENT_NAME = "Прізвище Ім'я"  # ← впишіть своє ім'я


def _page(title: str, body: str) -> str:
    """Мінімальна HTML-сторінка з навігацією (шаблонів у цій практичній ще немає)."""
    nav = " | ".join(
        f'<a href="{reverse(name)}">{label}</a>'
        for name, label in (("index", "Головна"), ("about", "Про проект"), ("contact", "Контакти"))
    )
    return (
        '<!DOCTYPE html><html lang="uk"><head><meta charset="UTF-8">'
        f"<title>{title}</title></head><body>"
        f"<nav>{nav}</nav><hr>{body}</body></html>"
    )


def index(request):
    """Головна сторінка."""
    body = (
        "<h1>Вітаємо на сайті mysite!</h1>"
        "<p>Це перший Django-проект, створений у практичній роботі №5.</p>"
        "<ul>"
        "<li>Django-проект створено командою <code>django-admin startproject</code></li>"
        "<li>Додаток <code>pages</code> зареєстровано в <code>INSTALLED_APPS</code></li>"
        "<li>Маршрути підключено через <code>include()</code></li>"
        "</ul>"
    )
    return HttpResponse(_page("Головна", body))


def about(request):
    """Сторінка 'Про проект'."""
    body = (
        "<h1>Про проект</h1>"
        f"<p><strong>Курс:</strong> {COURSE}</p>"
        f"<p><strong>Практична робота:</strong> №{PRACTICE_NUMBER}</p>"
        f"<p><strong>Студент:</strong> {STUDENT_NAME}</p>"
    )
    return HttpResponse(_page("Про проект", body))


def contact(request):
    """Контактна сторінка з параметрами запиту."""
    name = request.GET.get("name", "").strip()
    if name:
        # escape() — захист від XSS: ?name=<script>… виведеться як текст
        greeting = f"<h1>Вітаю, {escape(name)}!</h1><p>Дякуємо, що завітали на сторінку контактів.</p>"
    else:
        greeting = (
            "<h1>Контакти</h1>"
            "<p>Напишіть нам: info@mysite.example</p>"
            '<p>Підказка: додайте до адреси <code>?name=Олена</code>, щоб отримати привітання.</p>'
        )
    return HttpResponse(_page("Контакти", greeting))
