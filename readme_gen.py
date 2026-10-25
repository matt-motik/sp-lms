#!/usr/bin/env python
"""Генератор документации README из docstring."""

import ast
import re
import subprocess
from collections import defaultdict
from datetime import datetime
from pathlib import Path
from typing import Any

# ==================== НАСТРОЙКИ ====================
SOURCE_DIRS = ["catalog", "blog", "config", "users"]
EXCLUDE_DIRS = {".venv", "venv", "env", "__pycache__", "htmlcov", "tests", "docs", ".git", ".idea", ".vscode"}
EXCLUDE_FILES = {"media", "readme_gen.py", "setup.py", ".env", "db.sqlite3"}
README_FILE = "README.md"
DOCS_OUTPUT_DIR = Path("docs/api")
PROJECT_ROOT = Path(__file__).resolve().parent

# ===================================================


def extract_docstrings_from_file(filepath: Path) -> list[dict[str, Any]]:
    """Извлекает docstring из одного Python файла."""
    try:
        with open(filepath, encoding="utf-8") as f:
            content = f.read()

        tree = ast.parse(content)
        results = []

        for node in ast.walk(tree):
            if isinstance(node, ast.FunctionDef):
                if node.name.startswith("_"):
                    continue
                docstring = ast.get_docstring(node)
                if docstring:
                    first_line = docstring.strip().split("\n")[0]
                    results.append(
                        {
                            "type": "function",
                            "name": node.name,
                            "summary": first_line[:150],
                            "full_docstring": docstring,
                            "file": filepath.name,
                        }
                    )

            elif isinstance(node, ast.ClassDef):
                if node.name.startswith("_"):
                    continue
                docstring = ast.get_docstring(node)
                if docstring:
                    first_line = docstring.strip().split("\n")[0]
                    results.append(
                        {
                            "type": "class",
                            "name": node.name,
                            "summary": first_line[:150],
                            "full_docstring": docstring,
                            "file": filepath.name,
                        }
                    )

                for item in node.body:
                    if isinstance(item, ast.FunctionDef):
                        if item.name.startswith("_"):
                            continue
                        docstring = ast.get_docstring(item)
                        if docstring:
                            first_line = docstring.strip().split("\n")[0]
                            results.append(
                                {
                                    "type": "method",
                                    "name": f"{node.name}.{item.name}",
                                    "summary": first_line[:150],
                                    "full_docstring": docstring,
                                    "file": filepath.name,
                                }
                            )

        return results
    except Exception as e:
        print(f"  ⚠️ Ошибка в {filepath.name}: {e}")
        return []


def generate_api_table(all_docs: list[dict[str, Any]]) -> str:
    """Генерирует Markdown таблицу для раздела API с якорями для GitHub."""
    if not all_docs:
        return "| `—` | `—` | Документация не найдена |\n"

    by_file = defaultdict(list)
    for doc in all_docs:
        by_file[doc["file"]].append(doc)

    lines = []
    for file, docs in sorted(by_file.items()):
        base_name = file.replace(".py", "")
        link_path = DOCS_OUTPUT_DIR / f"{base_name}.md"
        link = str(link_path).replace("\\", "/")

        # Строка модуля — теперь это ссылка на файл с документацией
        lines.append(f"| [**`{file}`**]({link}) | | |")

        for doc in docs:
            icon = "🔧" if doc["type"] == "function" else "📦" if doc["type"] == "class" else "⚙️"
            # Оставляем якорь для GitHub
            doc_link = f"[{icon} {doc['name']}]({link}#{doc['name']})"
            lines.append(f"| | {doc_link} | {doc['summary']} |")

    return "\n".join(lines)


def generate_detailed_docs(all_docs: list[dict[str, Any]]) -> None:
    """Генерирует подробную документацию с HTML-якорями."""
    DOCS_OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

    by_file = defaultdict(list)
    for doc in all_docs:
        by_file[doc["file"]].append(doc)

    for file, docs in by_file.items():
        base_name = file.replace(".py", "")
        md_file = DOCS_OUTPUT_DIR / f"{base_name}.md"

        with open(md_file, "w", encoding="utf-8") as f:
            f.write(f"# Модуль: `{file}`\n\n")
            f.write(f"*Сгенерировано: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}*\n\n")
            f.write("---\n\n")

            for doc in docs:
                # HTML-якорь для GitHub (PyCharm его просто проигнорирует)
                f.write(f'<div id="{doc["name"]}"></div>\n\n')
                f.write(f"## {doc['name']}\n\n")
                f.write(f"**Тип:** {doc['type']}\n\n")
                f.write(f"**Кратко:** {doc['summary']}\n\n")

                f.write("### Полная документация\n\n")
                f.write("```python\n")
                f.write(doc["full_docstring"].strip())
                f.write("\n```\n\n")

                f.write("---\n\n")


def generate_project_structure() -> str:
    """Генерирует дерево проекта в формате Markdown."""

    def should_include(path: Path) -> bool:
        """Определяет, нужно ли включать файл или каталог в структуру."""
        relative_parts = path.relative_to(PROJECT_ROOT).parts

        # Скрытые файлы/каталоги и явно исключённые элементы не показываем.
        if any(part.startswith(".") for part in relative_parts):
            return False
        if any(part in EXCLUDE_DIRS for part in relative_parts):
            return False
        return path.name not in EXCLUDE_FILES

    def get_visible_items(directory: Path) -> list[Path]:
        """Возвращает отсортированные элементы каталога после фильтрации."""
        return sorted(
            (item for item in directory.iterdir() if should_include(item)),
            key=lambda p: (not p.is_dir(), p.name.lower()),
        )

    def get_tree(directory: Path, prefix: str = "") -> list[str]:
        """Рекурсивно строит дерево файлов и каталогов."""
        lines: list[str] = []
        items = get_visible_items(directory)

        for index, item in enumerate(items):
            is_last = index == len(items) - 1
            branch = "└── " if is_last else "├── "
            name = f"{item.name}/" if item.is_dir() else item.name

            lines.append(f"{prefix}{branch}{name}")

            if item.is_dir():
                child_prefix = prefix + ("    " if is_last else "│   ")
                lines.extend(get_tree(item, child_prefix))

        return lines

    tree_lines = ["```text", f"{PROJECT_ROOT.name}/"]
    tree_lines.extend(get_tree(PROJECT_ROOT))
    tree_lines.append("```")

    return "\n".join(tree_lines)


def run_tests_and_get_results_src() -> str:
    """Запускает pytest с coverage и возвращает форматированный вывод."""
    print("\n🧪 Запуск тестов с coverage...")

    try:
        # Запускаем pytest с coverage
        result = subprocess.run(
            ["uv", "run", "pytest"],
            capture_output=True,
            text=True,
            encoding="utf-8",
        )

        output = result.stdout + result.stderr

        # Парсим coverage summary
        coverage_summary = ""
        for line in output.split("\n"):
            if "TOTAL" in line or "Coverage" in line or "%" in line:
                coverage_summary += line + "\n"

        # Форматируем вывод для Markdown
        formatted_output = "### 📊 Результаты тестов SRC\n\n"
        formatted_output += "```\n"

        # Добавляем основную информацию
        if "FAILED" in output or "ERROR" in output:
            formatted_output += "❌ Некоторые тесты не прошли!\n\n"

        # Выводим summary coverage
        if coverage_summary:
            formatted_output += "📈 Покрытие кода:\n"
            formatted_output += coverage_summary + "\n"

        # Выводим последние строки с результатами
        lines = output.split("\n")
        test_lines = []
        for line in lines[-30:]:  # Последние 30 строк
            if any(keyword in line for keyword in ["PASSED", "FAILED", "ERROR", "test_", "===", "---"]):
                test_lines.append(line)

        if test_lines:
            formatted_output += "🎯 Результаты тестов src:\n"
            formatted_output += "\n".join(test_lines[-20:])  # Последние 20 строк

        formatted_output += "\n```\n\n"

        # Добавляем ссылку на HTML отчёт
        formatted_output += "> 📊 **HTML отчёт покрытия**: [`htmlcov/index.html`](htmlcov/src/index.html)\n\n"

        return formatted_output

    except subprocess.CalledProcessError as e:
        return f"```\n❌ Ошибка при запуске тестов: {e}\n```\n"
    except FileNotFoundError:
        return "```\n⚠️ Pytest не найден. Установите: poetry add --group dev pytest pytest-cov\n```\n"


def run_tests_and_get_results_main() -> str:
    """Запускает pytest с coverage и возвращает форматированный вывод."""
    print("\n🧪 Запуск тестов с coverage...")

    try:
        # Запускаем pytest с coverage
        result = subprocess.run(
            [
                "uv",
                "run",
                "pytest",
                "tests/test_main.py",
                "--cov=main",
                "--cov-report=term-missing",
                "--cov-report=html:htmlcov/main",
            ],
            capture_output=True,
            text=True,
            encoding="utf-8",
        )

        output = result.stdout + result.stderr

        # Парсим coverage summary
        coverage_summary = ""
        for line in output.split("\n"):
            if "TOTAL" in line or "Coverage" in line or "%" in line:
                coverage_summary += line + "\n"

        # Форматируем вывод для Markdown
        formatted_output = "### 📊 Результаты тестов main.py\n\n"
        formatted_output += "```\n"

        # Добавляем основную информацию
        if "FAILED" in output or "ERROR" in output:
            formatted_output += "❌ Некоторые тесты не прошли!\n\n"

        # Выводим summary coverage
        if coverage_summary:
            formatted_output += "📈 Покрытие кода:\n"
            formatted_output += coverage_summary + "\n"

        # Выводим последние строки с результатами
        lines = output.split("\n")
        test_lines = []
        for line in lines[-30:]:  # Последние 30 строк
            if any(keyword in line for keyword in ["PASSED", "FAILED", "ERROR", "test_", "===", "---"]):
                test_lines.append(line)

        if test_lines:
            formatted_output += "🎯 Результаты тестов main.py:\n"
            formatted_output += "\n".join(test_lines[-20:])  # Последние 20 строк

        formatted_output += "\n```\n\n"

        # Добавляем ссылку на HTML отчёт
        formatted_output += "> 📊 **HTML отчёт покрытия**: [`htmlcov/index.html`](htmlcov/main/index.html)\n\n"

        return formatted_output

    except subprocess.CalledProcessError as e:
        return f"```\n❌ Ошибка при запуске тестов: {e}\n```\n"
    except FileNotFoundError:
        return "```\n⚠️ Pytest не найден. Установите: poetry add --group dev pytest pytest-cov\n```\n"


def update_readme_with_api_table(api_table: str) -> bool:
    """Обновляет README.md, вставляя таблицу между маркерами."""
    if not Path(README_FILE).exists():
        print(f"❌ Файл {README_FILE} не найден!")
        return False

    with open(README_FILE, encoding="utf-8") as f:
        content = f.read()

    pattern = r"(<!-- СЕКЦИЯ_AUTO_API: СТАРТ -->).*?(<!-- СЕКЦИЯ_AUTO_API: КОНЕЦ -->)"
    docs_path = str(DOCS_OUTPUT_DIR).replace("\\", "/")

    new_section = f"""<!-- СЕКЦИЯ_AUTO_API: СТАРТ -->
<details>
<summary>📚 Документация API (развёрнуть)</summary>

*Этот раздел генерируется автоматически из docstring.*

| Модуль | Функция/Класс | Краткое описание |
|--------|---------------|------------------|
{api_table}

> 📘 **Полная документация** с примерами и описанием параметров доступна в папке [`{docs_path}`]({docs_path}).
</details>
<!-- СЕКЦИЯ_AUTO_API: КОНЕЦ -->"""

    if re.search(pattern, content, re.DOTALL):
        new_content = re.sub(pattern, new_section, content, flags=re.DOTALL)
        print("✅ Обновлена существующая секция API в README.md")
    else:
        new_content = content + "\n\n" + new_section
        print("⚠️ Маркеры не найдены, секция добавлена в конец README.md")

    with open(README_FILE, "w", encoding="utf-8") as f:
        f.write(new_content)

    return True


def update_readme_with_project_structure(structure: str) -> bool:
    """Обновляет README.md, вставляя структуру проекта между маркерами."""
    if not Path(README_FILE).exists():
        print(f"❌ Файл {README_FILE} не найден!")
        return False

    with open(README_FILE, encoding="utf-8") as f:
        content = f.read()

    pattern = r"(<!-- СЕКЦИЯ_AUTO_STRUCTURE: СТАРТ -->).*?(<!-- СЕКЦИЯ_AUTO_STRUCTURE: КОНЕЦ -->)"

    new_section = f"""<!-- СЕКЦИЯ_AUTO_STRUCTURE: СТАРТ -->
<details>
<summary>📁 Структура проекта (развёрнуть)</summary>

*Этот раздел генерируется автоматически.*

{structure}

</details>
<!-- СЕКЦИЯ_AUTO_STRUCTURE: КОНЕЦ -->"""

    if re.search(pattern, content, re.DOTALL):
        new_content = re.sub(pattern, new_section, content, flags=re.DOTALL)
        print("✅ Обновлена существующая секция структуры в README.md")
    else:
        # Вставляем после секции API
        api_pattern = r"(<!-- СЕКЦИЯ_AUTO_API: КОНЕЦ -->)"
        if re.search(api_pattern, content):
            new_content = re.sub(api_pattern, f"<!-- СЕКЦИЯ_AUTO_API: КОНЕЦ -->\n\n{new_section}", content, count=1)
            print("✅ Секция структуры добавлена после секции API")
        else:
            new_content = content + "\n\n" + new_section
            print("⚠️ Маркеры API не найдены, структура добавлена в конец README.md")

    with open(README_FILE, "w", encoding="utf-8") as f:
        f.write(new_content)

    return True


def update_readme_with_test_section(test_results: str) -> bool:
    """Обновляет README.md, вставляя результаты тестов между маркерами."""
    if not Path(README_FILE).exists():
        print(f"❌ Файл {README_FILE} не найден!")
        return False

    with open(README_FILE, encoding="utf-8") as f:
        content = f.read()

    pattern = r"(<!-- СЕКЦИЯ_AUTO_TEST: СТАРТ -->).*?(<!-- СЕКЦИЯ_AUTO_TEST: КОНЕЦ -->)"

    # Используем lambda функцию для замены, чтобы re.sub не интерпретировал test_results
    def replace_section(match: re.Match) -> str:
        return f"""<!-- СЕКЦИЯ_AUTO_TEST: СТАРТ -->
<details>
<summary>📊 Результаты тестов и покрытие (развёрнуть)</summary>
{test_results}
</details>
<!-- СЕКЦИЯ_AUTO_TEST: КОНЕЦ -->"""

    if re.search(pattern, content, re.DOTALL):
        new_content = re.sub(pattern, replace_section, content, flags=re.DOTALL)
        print("✅ Обновлена существующая секция тестирования в README.md")
        with open(README_FILE, "w", encoding="utf-8") as f:
            f.write(new_content)
        return True
    else:
        print("⚠️ Маркеры <!-- СЕКЦИЯ_AUTO_TEST: СТАРТ/КОНЕЦ --> не найдены в README.md")
        print("   Добавьте их вручную в раздел 'Тестирование'")
        return False


def main() -> None:
    """Проверяет докстринги и обновляет раздел README."""
    print("=" * 50)
    print("🔍 Генератор документации README из docstring")
    print("=" * 50)

    # ===== 1. Поиск Python файлов =====
    py_files = []

    for source_dir in SOURCE_DIRS:
        source_path = Path(source_dir)
        if not source_path.exists():
            print(f"⚠️ Папка {source_dir} не найдена, пропускаем")
            continue

        for py_file in source_path.rglob("*.py"):
            if any(excluded in py_file.parts for excluded in EXCLUDE_DIRS):
                continue
            if py_file.name in EXCLUDE_FILES:
                continue
            py_files.append(py_file)

    for py_file in Path(".").glob("*.py"):
        if py_file.name in EXCLUDE_FILES:
            continue
        if any(excluded in py_file.parts for excluded in EXCLUDE_DIRS):
            continue
        py_files.append(py_file)

    print(f"📁 Найдено Python файлов: {len(py_files)}")

    if not py_files:
        print("❌ Нет Python файлов для обработки!")
        return

    # ===== 2. Извлечение документации =====
    all_docs = []
    for py_file in py_files:
        docs = extract_docstrings_from_file(py_file)
        if docs:
            print(f"  ✓ {py_file}: {len(docs)} элементов")
            all_docs.extend(docs)

    if not all_docs:
        print("⚠️ Не найдено docstring в файлах.")
        return

    print(f"\n📊 Всего документировано: {len(all_docs)} элементов")

    # ===== 3. Генерация таблицы API =====
    print("\n📝 Генерация таблицы API...")
    api_table = generate_api_table(all_docs)

    if update_readme_with_api_table(api_table):
        print("✅ README.md обновлён (секция API)")

    # ===== 4. Генерация структуры проекта =====
    print("\n📁 Генерация структуры проекта...")
    project_structure = generate_project_structure()

    if update_readme_with_project_structure(project_structure):
        print("✅ README.md обновлён (секция структуры)")

    # ===== 5. Генерация детальной документации =====
    print(f"\n📚 Генерация детальной документации в {DOCS_OUTPUT_DIR}...")
    generate_detailed_docs(all_docs)
    print(f"✅ Создано {len(all_docs)} страниц документации")

    # ===== 6. Запуск тестов и обновление секции =====
    print("\n" + "=" * 50)
    test_results_src = run_tests_and_get_results_src()
    # test_results_main = run_tests_and_get_results_main()
    update_readme_with_test_section(test_results_src)
    print("=" * 50)

    print("\n" + "=" * 50)
    print("🎉 Готово!")
    print("=" * 50)


if __name__ == "__main__":
    main()
