"""Головний файл Flask-додатка."""

import importlib.metadata

from flask import Flask, jsonify, request, url_for
from markupsafe import escape

from config import config_by_name


def create_app(config_name: str = "default") -> Flask:
    """Фабрика додатка Flask.

    Args:
        config_name: ім'я конфігурації ('development', 'production').

    Returns:
        Налаштований екземпляр Flask.
    """
    app = Flask(__name__)
    app.config.from_object(config_by_name[config_name])
    if config_name == "production" and not app.config["SECRET_KEY"]:
        raise RuntimeError("Для production задайте змінну оточення SECRET_KEY")
    register_routes(app)
    return app


def _page(title: str, body: str) -> str:
    """Мінімальна HTML-сторінка зі стилями зі static/style.css."""
    return (
        '<!DOCTYPE html><html lang="uk"><head><meta charset="UTF-8">'
        f'<title>{title}</title>'
        f'<link rel="stylesheet" href="{url_for("static", filename="style.css")}">'
        f"</head><body><main>{body}</main></body></html>"
    )


def register_routes(app: Flask):
    """Реєструє маршрути додатка."""

    @app.route("/")
    def index():
        """Головна сторінка."""
        body = (
            "<h1>Вітаємо у myflaskapp!</h1>"
            "<p>Мінімальний Flask-додаток із патерном Application Factory.</p>"
            "<ul>"
            f'<li><a href="{url_for("about")}">Про додаток</a></li>'
            f'<li><a href="{url_for("api_info")}">API: інформація у JSON</a></li>'
            f'<li><a href="{url_for("greet", name="Олена")}">Привітання: /greet/Олена</a></li>'
            f'<li><a href="{url_for("greet")}?name=Іван">Привітання з query: /greet?name=Іван</a></li>'
            "</ul>"
        )
        return _page("myflaskapp", body)

    @app.route("/about")
    def about():
        """Сторінка 'Про додаток'."""
        body = (
            "<h1>Про додаток</h1>"
            f"<p>Фреймворк: Flask {importlib.metadata.version('flask')}</p>"
            f"<p>Конфігурація: DEBUG = {app.config['DEBUG']}</p>"
            "<p>Структура: app.py (фабрика й маршрути), config.py (класи конфігурацій), "
            "static/ (CSS), templates/ (шаблони — з'являться в наступних роботах).</p>"
            f'<p><a href="{url_for("index")}">← На головну</a></p>'
        )
        return _page("Про додаток", body)

    @app.route("/api/info")
    def api_info():
        """API-ендпоінт з інформацією у JSON."""
        routes = sorted(
            (
                {
                    "rule": rule.rule,
                    "endpoint": rule.endpoint,
                    "methods": sorted(rule.methods - {"HEAD", "OPTIONS"}),
                }
                for rule in app.url_map.iter_rules()
                if rule.endpoint != "static"
            ),
            key=lambda r: r["rule"],
        )
        return jsonify(
            framework="Flask",
            version=importlib.metadata.version("flask"),
            debug=app.debug,
            routes=routes,
        )

    @app.route("/greet")
    @app.route("/greet/<name>")
    def greet(name=None):
        """Маршрут з динамічним параметром та query-параметром."""
        if name is None:
            name = request.args.get("name", "Гість")
        # escape() — захист від XSS у рядку, що повертається як HTML
        return _page("Привітання", f"<h1>Привіт, {escape(name)}!</h1>"
                                   f'<p><a href="{url_for("index")}">← На головну</a></p>')


if __name__ == "__main__":
    application = create_app("development")
    application.run(debug=True, port=5000)
