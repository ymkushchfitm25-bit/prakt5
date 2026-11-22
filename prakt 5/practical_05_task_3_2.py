"""Порівняльний аналіз структури Django та Flask проектів."""

import os

IGNORED_DIRS = {"__pycache__", "venv", "venv2", ".venv", ".git", ".idea", ".vscode", "instance"}
IGNORED_FILES = {"db.sqlite3", ".DS_Store"}
IGNORED_SUFFIXES = (".pyc", ".pyo")


def _is_ignored(name: str, is_dir: bool) -> bool:
    if is_dir:
        return name in IGNORED_DIRS
    return name in IGNORED_FILES or name.endswith(IGNORED_SUFFIXES)


def scan_directory(path: str, prefix: str = "") -> list[str]:
    """Рекурсивно сканує каталог та повертає дерево файлів.

    Args:
        path: шлях до каталогу.
        prefix: відступ для форматування дерева.

    Returns:
        Список рядків зі структурою каталогу.
    """
    tree = []
    entries = []
    for name in os.listdir(path):
        full = os.path.join(path, name)
        is_dir = os.path.isdir(full)
        if not _is_ignored(name, is_dir):
            entries.append((not is_dir, name.lower(), name, full, is_dir))  # спершу каталоги
    entries.sort()

    for index, (_, _, name, full, is_dir) in enumerate(entries):
        last = index == len(entries) - 1
        connector = "└── " if last else "├── "
        tree.append(f"{prefix}{connector}{name}{'/' if is_dir else ''}")
        if is_dir:
            tree.extend(scan_directory(full, prefix + ("    " if last else "│   ")))
    return tree


def analyze_project(path: str) -> dict:
    """Аналізує проект та збирає статистику.

    Args:
        path: кореневий каталог проекту.

    Returns:
        Словник зі статистикою: кількість файлів .py, .html, .css,
        загальний розмір, список каталогів.
    """
    stats = {
        "py_files": 0,
        "html_files": 0,
        "css_files": 0,
        "other_files": 0,
        "py_lines": 0,
        "total_size": 0,
        "directories": [],
    }
    for root, dirs, files in os.walk(path):
        dirs[:] = sorted(d for d in dirs if not _is_ignored(d, True))
        rel = os.path.relpath(root, path)
        if rel != ".":
            stats["directories"].append(rel.replace(os.sep, "/"))
        for name in files:
            if _is_ignored(name, False):
                continue
            full = os.path.join(root, name)
            stats["total_size"] += os.path.getsize(full)
            if name.endswith(".py"):
                stats["py_files"] += 1
                with open(full, encoding="utf-8", errors="replace") as f:
                    stats["py_lines"] += sum(1 for line in f if line.strip())
            elif name.endswith(".html"):
                stats["html_files"] += 1
            elif name.endswith(".css"):
                stats["css_files"] += 1
            else:
                stats["other_files"] += 1
    return stats


def compare_projects(django_path: str, flask_path: str):
    """Порівнює два проекти та виводить таблицю відмінностей.

    Args:
        django_path: шлях до Django-проекту.
        flask_path: шлях до Flask-проекту.
    """
    print("=" * 60)
    print("ПОРІВНЯННЯ СТРУКТУРИ ПРОЕКТІВ")
    print("=" * 60)

    print(f"\n--- Django ({django_path}) ---")
    print(f"{django_path}/")
    for line in scan_directory(django_path):
        print(line)
    django_stats = analyze_project(django_path)

    print(f"\n--- Flask ({flask_path}) ---")
    print(f"{flask_path}/")
    for line in scan_directory(flask_path):
        print(line)
    flask_stats = analyze_project(flask_path)

    rows = [
        ("Файли .py", "py_files"),
        ("Непорожні рядки .py", "py_lines"),
        ("Файли .html", "html_files"),
        ("Файли .css", "css_files"),
        ("Інші файли", "other_files"),
        ("Каталоги", None),
        ("Розмір (байт)", "total_size"),
    ]
    print(f"\n| {'Характеристика':<20} | {'Django':>8} | {'Flask':>8} |")
    print(f"|{'-' * 22}|{'-' * 10}|{'-' * 10}|")
    for title, key in rows:
        if key is None:
            d, f = len(django_stats["directories"]), len(flask_stats["directories"])
        else:
            d, f = django_stats[key], flask_stats[key]
        print(f"| {title:<20} | {d:>8,} | {f:>8,} |".replace(",", " "))

    print(f"\nКаталоги Django: {', '.join(django_stats['directories']) or '—'}")
    print(f"Каталоги Flask:  {', '.join(flask_stats['directories']) or '—'}")


def main():
    django_path = "mysite"
    flask_path = "myflaskapp"

    for path in [django_path, flask_path]:
        if not os.path.isdir(path):
            print(f"Каталог '{path}' не знайдено. Спершу виконайте попередні завдання.")
            return

    compare_projects(django_path, flask_path)


if __name__ == "__main__":
    main()
