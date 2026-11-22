"""Генератор requirements.txt з перевіркою залежностей.

Звичайний запуск (у першому середовищі venv):
    python practical_05_task_1_2.py
        -> створює requirements.txt і перевіряє його

Перевірка відтворення (у другому середовищі venv2 після pip install -r requirements.txt):
    python practical_05_task_1_2.py --output requirements_venv2.txt --compare requirements.txt
        -> знімає список пакетів venv2 і порівнює з оригінальним файлом
"""

import argparse
import importlib.metadata
import json
import re
import subprocess
import sys
from pathlib import Path

SYSTEM_PACKAGES = {"pip", "setuptools", "wheel"}


def normalize(name: str) -> str:
    """Нормалізує назву пакета за PEP 503 (Flask-WTF == flask_wtf == flask.wtf)."""
    return re.sub(r"[-_.]+", "-", name).lower()


def get_installed_packages() -> list[dict]:
    """Повертає список встановлених пакетів з версіями.

    Returns:
        Список словників {'name': ..., 'version': ...}.
    """
    result = subprocess.run(
        [sys.executable, "-m", "pip", "list", "--format=json"],
        capture_output=True, text=True,
    )
    if result.returncode != 0:
        print(f"Помилка виконання pip list:\n{result.stderr}", file=sys.stderr)
        return []
    try:
        data = json.loads(result.stdout)
    except json.JSONDecodeError as exc:
        print(f"Не вдалося розібрати JSON від pip: {exc}", file=sys.stderr)
        return []
    return [{"name": item["name"], "version": item["version"]} for item in data]


def generate_requirements(packages: list[dict], filename: str = "requirements.txt") -> int:
    """Записує пакети у файл requirements.txt.

    Args:
        packages: список словників з ключами 'name' та 'version'.
        filename: ім'я файлу для запису.

    Returns:
        Кількість записаних пакетів.
    """
    filtered = sorted(
        (p for p in packages if normalize(p["name"]) not in SYSTEM_PACKAGES),
        key=lambda p: normalize(p["name"]),
    )
    lines = [f"{p['name']}=={p['version']}" for p in filtered]
    Path(filename).write_text("\n".join(lines) + "\n", encoding="utf-8")
    return len(lines)


def read_requirements(filename: str) -> dict[str, str]:
    """Читає файл формату package==version у словник {назва: версія}.

    Raises:
        FileNotFoundError: якщо файлу немає.
    """
    requirements = {}
    for raw in Path(filename).read_text(encoding="utf-8").splitlines():
        line = raw.split("#", 1)[0].strip()
        if not line or line.startswith("-"):
            continue  # порожні рядки, коментарі, опції на кшталт -r / --index-url
        name, sep, version = line.partition("==")
        requirements[normalize(name.strip())] = version.strip() if sep else ""
    return requirements


def verify_requirements(filename: str = "requirements.txt") -> bool:
    """Перевіряє, чи всі пакети з requirements.txt встановлені.

    Args:
        filename: шлях до файлу requirements.txt.

    Returns:
        True, якщо всі залежності задоволені.
    """
    try:
        requirements = read_requirements(filename)
    except FileNotFoundError:
        print(f"Файл {filename} не знайдено — нічого перевіряти.")
        return False

    problems = []
    for name, wanted in requirements.items():
        try:
            installed = importlib.metadata.version(name)
        except importlib.metadata.PackageNotFoundError:
            problems.append(f"{name}: не встановлено (потрібно {wanted or 'будь-яка версія'})")
            continue
        if wanted and installed != wanted:
            problems.append(f"{name}: встановлено {installed}, потрібно {wanted}")
    for problem in problems:
        print(f"  ✗ {problem}")
    print(f"Перевірено {len(requirements)} пакетів з {filename}, розбіжностей: {len(problems)}")
    return not problems


def compare_requirement_files(first: str, second: str) -> bool:
    """Порівнює два requirements-файли (наприклад, з venv і venv2)."""
    try:
        a, b = read_requirements(first), read_requirements(second)
    except FileNotFoundError as exc:
        print(f"Файл {exc.filename} не знайдено.")
        return False
    only_a = sorted(set(a) - set(b))
    only_b = sorted(set(b) - set(a))
    different = sorted(n for n in set(a) & set(b) if a[n] != b[n])
    print(f"\n=== Порівняння {first} ↔ {second} ===")
    print(f"  Пакетів: {len(a)} ↔ {len(b)}")
    for name in only_a:
        print(f"  лише в {first}: {name}=={a[name]}")
    for name in only_b:
        print(f"  лише в {second}: {name}=={b[name]}")
    for name in different:
        print(f"  різні версії {name}: {a[name]} ↔ {b[name]}")
    identical = not (only_a or only_b or different)
    print("  Середовища ІДЕНТИЧНІ ✓" if identical else "  Середовища відрізняються ✗")
    return identical


def main():
    parser = argparse.ArgumentParser(description="Генерація та перевірка requirements.txt")
    parser.add_argument("--output", default="requirements.txt", help="куди записати список пакетів")
    parser.add_argument("--compare", metavar="FILE", help="порівняти з іншим requirements-файлом")
    args = parser.parse_args()

    packages = get_installed_packages()
    print(f"Середовище: {sys.prefix}")
    print(f"Знайдено {len(packages)} встановлених пакетів\n")

    for pkg in packages[:10]:
        print(f"  {pkg['name']}=={pkg['version']}")
    if len(packages) > 10:
        print(f"  ... та ще {len(packages) - 10}")

    written = generate_requirements(packages, args.output)
    print(f"\nФайл {args.output} створено ({written} пакетів, без pip/setuptools/wheel)")

    ok = verify_requirements(args.output)
    print(f"Перевірка залежностей: {'✓ Усе OK' if ok else '✗ Є розбіжності'}")

    if args.compare:
        compare_requirement_files(args.compare, args.output)


if __name__ == "__main__":
    main()
