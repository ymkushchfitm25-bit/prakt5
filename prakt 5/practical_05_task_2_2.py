"""Аналізатор конфігурації Django-проекту.

settings.py розбирається через модуль ast (синтаксичне дерево), а не
імпортується: так не потрібен встановлений Django і не виконується код
файлу. Значення, які не є літералами (BASE_DIR / 'db.sqlite3',
os.environ.get(...)), розпізнаються за структурою виразу.
"""

import ast
import os
import sys


def _assignments(settings_path: str) -> dict[str, ast.expr]:
    """Повертає {ІМ'Я_ЗМІННОЇ: вузол-вираз} для всіх присвоєнь верхнього рівня."""
    with open(settings_path, encoding="utf-8") as f:
        tree = ast.parse(f.read(), filename=settings_path)
    result = {}
    for node in tree.body:
        if isinstance(node, ast.Assign):
            for target in node.targets:
                if isinstance(target, ast.Name):
                    result[target.id] = node.value
        elif isinstance(node, ast.AnnAssign) and isinstance(node.target, ast.Name) and node.value:
            result[node.target.id] = node.value
    return result


def _literal(node: ast.expr | None, default=None):
    """Значення літерала або default, якщо вираз не є літералом."""
    if node is None:
        return default
    try:
        return ast.literal_eval(node)
    except ValueError:
        return default


def _database_engine(node: ast.expr | None) -> str:
    """Витягує DATABASES['default']['ENGINE'] навіть якщо NAME — не літерал."""
    if not isinstance(node, ast.Dict):
        return "не визначено"
    for key, value in zip(node.keys, node.values):
        if _literal(key) == "default" and isinstance(value, ast.Dict):
            for k, v in zip(value.keys, value.values):
                if _literal(k) == "ENGINE":
                    engine = _literal(v, "невідомо")
                    return f"{engine.rsplit('.', 1)[-1]} ({engine})"
    return "не визначено"


def analyze_settings(settings_path: str) -> dict:
    """Аналізує файл settings.py та повертає ключові параметри.

    Args:
        settings_path: шлях до файлу settings.py.

    Returns:
        Словник з аналізом конфігурації.
    """
    values = _assignments(settings_path)
    apps = _literal(values.get("INSTALLED_APPS"), [])
    own_apps = [a for a in apps if not a.startswith("django.")]
    return {
        "DEBUG": _literal(values.get("DEBUG"), "вираз (не літерал)"),
        "INSTALLED_APPS": f"{len(apps)} додатків, власні: {own_apps or 'немає'}",
        "DATABASES": _database_engine(values.get("DATABASES")),
        "LANGUAGE_CODE": _literal(values.get("LANGUAGE_CODE"), "не задано"),
        "TIME_ZONE": _literal(values.get("TIME_ZONE"), "не задано"),
        "MIDDLEWARE": f"{len(_literal(values.get('MIDDLEWARE'), []))} компонентів",
        "ALLOWED_HOSTS": _literal(values.get("ALLOWED_HOSTS"), "вираз (не літерал)"),
    }


def _reads_environment(node: ast.expr) -> bool:
    """Чи містить вираз звернення до os.environ / os.getenv."""
    for sub in ast.walk(node):
        if isinstance(sub, ast.Attribute) and sub.attr in ("environ", "getenv"):
            return True
    return False


def check_security(settings_path: str) -> list[str]:
    """Перевіряє базову безпеку конфігурації.

    Args:
        settings_path: шлях до файлу settings.py.

    Returns:
        Список попереджень безпеки.
    """
    warnings = []
    values = _assignments(settings_path)

    # 1. DEBUG = True показує трасування й налаштування будь-кому
    debug = values.get("DEBUG")
    if debug is not None and _literal(debug) is True:
        warnings.append("DEBUG = True — небезпечно для production: відвідувачі бачитимуть "
                        "трасування помилок і фрагменти налаштувань")

    # 2. SECRET_KEY має братися зі змінної оточення, а не з коду
    secret = values.get("SECRET_KEY")
    if secret is None:
        warnings.append("SECRET_KEY не визначено")
    elif not _reads_environment(secret):
        value = _literal(secret, "")
        note = " (стандартний ключ django-insecure-…)" if str(value).startswith("django-insecure") else ""
        warnings.append(f"SECRET_KEY захардкоджено у файлі{note} — винесіть у "
                        "os.environ.get('DJANGO_SECRET_KEY')")

    # 3. Порожній ALLOWED_HOSTS: при DEBUG=False Django відхилятиме всі запити
    hosts = values.get("ALLOWED_HOSTS")
    if hosts is not None and _literal(hosts) == []:
        warnings.append("ALLOWED_HOSTS порожній — у production (DEBUG=False) сайт повертатиме "
                        "400 Bad Request; вкажіть домени, напр. ['example.com']")
    return warnings


def main():
    settings_path = sys.argv[1] if len(sys.argv) > 1 else "mysite/mysite/settings.py"
    if not os.path.exists(settings_path):
        print(f"Файл {settings_path} не знайдено")
        sys.exit(1)

    config = analyze_settings(settings_path)
    print("=== Аналіз конфігурації Django ===\n")
    for key, value in config.items():
        print(f"  {key}: {value}")

    print("\n=== Перевірка безпеки ===\n")
    warnings = check_security(settings_path)
    if warnings:
        for w in warnings:
            print(f"  ⚠ {w}")
    else:
        print("  Попереджень не знайдено")


if __name__ == "__main__":
    main()
