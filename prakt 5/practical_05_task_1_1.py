"""Скрипт перевірки середовища розробки."""

import importlib
import importlib.metadata
import sys

MIN_VERSION = (3, 10)


def check_python_version() -> bool:
    """Перевіряє версію Python (потрібна >= 3.10)."""
    version = sys.version_info
    print(f"Python {version.major}.{version.minor}.{version.micro}")
    if version[:2] < MIN_VERSION:
        print(f"  ⚠ Потрібен Python {MIN_VERSION[0]}.{MIN_VERSION[1]} або новіший — "
              "оновіть інтерпретатор.")
        return False
    print(f"  Версія підходить (>= {MIN_VERSION[0]}.{MIN_VERSION[1]}) ✓")
    return True


def check_virtualenv() -> bool:
    """Перевіряє, чи скрипт запущено всередині віртуального середовища.

    У venv sys.prefix вказує на каталог середовища, а sys.base_prefix — на
    системний Python. Це той самий факт, що показують `which python`
    (Linux/macOS) або `where python` (Windows).
    """
    in_venv = sys.prefix != sys.base_prefix
    print(f"\nІнтерпретатор: {sys.executable}")
    if in_venv:
        print(f"  Віртуальне середовище активне: {sys.prefix} ✓")
    else:
        print("  ⚠ Віртуальне середовище НЕ активне (використовується системний Python)")
    return in_venv


def check_package(package_name: str) -> bool:
    """Перевіряє, чи встановлено пакет, і виводить його версію.

    Args:
        package_name: назва пакета для перевірки.

    Returns:
        True, якщо пакет встановлено.
    """
    try:
        module = importlib.import_module(package_name)
    except ImportError:
        print(f"  {package_name}: НЕ ВСТАНОВЛЕНО ✗")
        return False
    try:
        # Надійніше за __version__: атрибут є не в усіх пакетах (у Flask 3.1 застарів)
        version = importlib.metadata.version(package_name)
    except importlib.metadata.PackageNotFoundError:
        version = getattr(module, "__version__", "невідома")
    print(f"  {package_name}: {version} ✓")
    return True


def main():
    check_python_version()
    check_virtualenv()

    print("\nВстановлені пакети:")
    packages = ["django", "flask"]
    results = {pkg: check_package(pkg) for pkg in packages}

    installed = [pkg for pkg, ok in results.items() if ok]
    missing = [pkg for pkg, ok in results.items() if not ok]
    print(f"\nПідсумок: встановлено {len(installed)} з {len(packages)}"
          + (f", відсутні: {', '.join(missing)}" if missing else ""))
    if missing:
        print("Для встановлення виконайте:")
        print(f"  pip install {' '.join(missing)}")
    else:
        print("Усе необхідне встановлено ✓")


if __name__ == "__main__":
    main()
