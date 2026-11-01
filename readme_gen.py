#!/usr/bin/env python
"""Генератор документации README из docstring."""

import ast
import re
import shutil
import subprocess
from collections import defaultdict
from datetime import datetime
from pathlib import Path
from typing import Any

# ==================== НАСТРОЙКИ ====================
PROJECT_ROOT = Path(__file__).resolve().parent
# Пустой список = искать автоматически все пакеты (папки с __init__.py) в корне проекта
SOURCE_DIRS: list[str] = []
EXCLUDE_DIRS = {
    ".venv",
    "venv",
    "env",
    "__pycache__",
    "htmlcov",
    "tests",
    "docs",
    "media",
    "migrations",
    "node_modules",
    ".git",
    ".idea",
    ".vscode",
}
EXCLUDE_FILES = {"readme_gen.py", "setup.py", ".env", "db.sqlite3"}
README_FILE = PROJECT_ROOT / "README.md"
DOCS_OUTPUT_DIR = Path("docs/api")
# ===================================================


def find_source_dirs() -> list[Path]:
    """Возвращает папки с исходниками: из SOURCE_DIRS или все пакеты в корне проекта."""
    if SOURCE_DIRS:
        return [PROJECT_ROOT / name for name in SOURCE_DIRS]
    return sorted(
        item
        for item in PROJECT_ROOT.iterdir()
        if item.is_dir()
        and not item.name.startswith(".")
        and item.name not in EXCLUDE_DIRS
        and (item / "__init__.py").exists()
    )


def find_python_files() -> list[Path]:
    """Собирает Python-файлы из папок с исходниками и корня проекта."""
    py_files: list[Path] = []

    for source_path in find_source_dirs():
        if not source_path.exists():
            print(f"⚠️ Папка {source_path.name} не найдена, пропускаем")
            continue
        for py_file in sorted(source_path.rglob("*.py")):
            relative_parts = py_file.relative_to(PROJECT_ROOT).parts
            if any(part in EXCLUDE_DIRS for part in relative_parts):
                continue
            if py_file.name in EXCLUDE_FILES:
                continue
            py_files.append(py_file)

    for py_file in sorted(PROJECT_ROOT.glob("*.py")):
        if py_file.name not in EXCLUDE_FILES:
            py_files.append(py_file)

    return py_files


def make_doc(kind: str, name: str, docstring: str, module: str) -> dict[str, Any]:
    """Формирует запись документации для одного объекта."""
    return {
        "type": kind,
        "name": name,
        "summary": docstring.strip().split("\n")[0][:150],
        "full_docstring": docstring,
        "file": module,
    }


def extract_from_class(node: ast.ClassDef, prefix: str, module: str) -> list[dict[str, Any]]:
    """Извлекает docstring класса, его методов и вложенных классов (например, Meta)."""
    results: list[dict[str, Any]] = []
    name = f"{prefix}{node.name}"

    docstring = ast.get_docstring(node)
    if docstring:
        results.append(make_doc("class", name, docstring, module))

    for item in node.body:
        if isinstance(item, ast.FunctionDef | ast.AsyncFunctionDef) and not item.name.startswith("_"):
            method_doc = ast.get_docstring(item)
            if method_doc:
                results.append(make_doc("method", f"{name}.{item.name}", method_doc, module))
        elif isinstance(item, ast.ClassDef) and not item.name.startswith("_"):
            results.extend(extract_from_class(item, f"{name}.", module))

    return results


def extract_docstrings_from_file(filepath: Path) -> list[dict[str, Any]]:
    """Извлекает docstring функций и классов верхнего уровня из одного Python-файла."""
    module = filepath.relative_to(PROJECT_ROOT).as_posix()
    try:
        tree = ast.parse(filepath.read_text(encoding="utf-8"))
    except (SyntaxError, UnicodeDecodeError) as e:
        print(f"  ⚠️ Ошибка в {module}: {e}")
        return []

    results: list[dict[str, Any]] = []
    for node in tree.body:
        if getattr(node, "name", "").startswith("_"):
            continue
        if isinstance(node, ast.FunctionDef | ast.AsyncFunctionDef):
            docstring = ast.get_docstring(node)
            if docstring:
                results.append(make_doc("function", node.name, docstring, module))
        elif isinstance(node, ast.ClassDef):
            results.extend(extract_from_class(node, "", module))

    return results


def doc_link_for(module: str) -> str:
    """Возвращает путь к markdown-файлу модуля относительно README: lms/models.py -> docs/api/lms/models.md."""
    return (DOCS_OUTPUT_DIR / Path(module).with_suffix(".md")).as_posix()


def anchor_for(name: str) -> str:
    """Возвращает HTML-якорь для объекта."""
    return name.replace(".", "-")


def group_by_module(all_docs: list[dict[str, Any]]) -> dict[str, list[dict[str, Any]]]:
    """Группирует записи документации по пути модуля."""
    by_file: dict[str, list[dict[str, Any]]] = defaultdict(list)
    for doc in all_docs:
        by_file[doc["file"]].append(doc)
    return dict(sorted(by_file.items()))


def generate_api_table(all_docs: list[dict[str, Any]]) -> str:
    """Генерирует Markdown-таблицу для раздела API с якорями для GitHub."""
    if not all_docs:
        return "| `—` | `—` | Документация не найдена |"

    icons = {"function": "🔧", "class": "📦", "method": "⚙️"}
    lines = []
    for module, docs in group_by_module(all_docs).items():
        link = doc_link_for(module)
        lines.append(f"| [**`{module}`**]({link}) | | |")
        for doc in docs:
            doc_link = f"[{icons[doc['type']]} {doc['name']}]({link}#{anchor_for(doc['name'])})"
            lines.append(f"| | {doc_link} | {doc['summary']} |")

    return "\n".join(lines)


def generate_detailed_docs(all_docs: list[dict[str, Any]]) -> int:
    """Пересоздаёт папку с подробной документацией и возвращает число созданных файлов."""
    docs_dir = PROJECT_ROOT / DOCS_OUTPUT_DIR
    if docs_dir.exists():
        shutil.rmtree(docs_dir)

    modules = group_by_module(all_docs)
    for module, docs in modules.items():
        md_file = PROJECT_ROOT / doc_link_for(module)
        md_file.parent.mkdir(parents=True, exist_ok=True)

        parts = [
            f"# Модуль: `{module}`\n",
            f"*Сгенерировано: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}*\n",
            "---\n",
        ]
        for doc in docs:
            parts.extend(
                [
                    f'<div id="{anchor_for(doc["name"])}"></div>\n',
                    f"## {doc['name']}\n",
                    f"**Тип:** {doc['type']}\n",
                    f"**Кратко:** {doc['summary']}\n",
                    "### Полная документация\n",
                    f"```text\n{doc['full_docstring'].strip()}\n```\n",
                    "---\n",
                ]
            )
        md_file.write_text("\n".join(parts), encoding="utf-8")

    return len(modules)


def generate_project_structure() -> str:
    """Генерирует дерево проекта в формате Markdown."""

    def should_include(path: Path) -> bool:
        """Определяет, нужно ли включать файл или каталог в структуру."""
        relative_parts = path.relative_to(PROJECT_ROOT).parts
        if any(part.startswith(".") for part in relative_parts):
            return False
        if any(part in EXCLUDE_DIRS - {"docs", "migrations", "tests"} for part in relative_parts):
            return False
        return path.name not in EXCLUDE_FILES - {"readme_gen.py"}

    def get_tree(directory: Path, prefix: str = "") -> list[str]:
        """Рекурсивно строит дерево файлов и каталогов."""
        lines: list[str] = []
        items = sorted(
            (item for item in directory.iterdir() if should_include(item)),
            key=lambda p: (not p.is_dir(), p.name.lower()),
        )
        for index, item in enumerate(items):
            is_last = index == len(items) - 1
            lines.append(f"{prefix}{'└── ' if is_last else '├── '}{item.name}{'/' if item.is_dir() else ''}")
            # Папку docs/api не разворачиваем: там только сгенерированные файлы
            if item.is_dir() and item.relative_to(PROJECT_ROOT).as_posix() != DOCS_OUTPUT_DIR.as_posix():
                lines.extend(get_tree(item, prefix + ("    " if is_last else "│   ")))
        return lines

    return "\n".join(["```text", f"{PROJECT_ROOT.name}/", *get_tree(PROJECT_ROOT), "```"])


def has_tests() -> bool:
    """Проверяет, есть ли в проекте файлы тестов."""
    for path in PROJECT_ROOT.rglob("test*.py"):
        relative_parts = path.relative_to(PROJECT_ROOT).parts
        if not any(part in EXCLUDE_DIRS - {"tests"} or part.startswith(".") for part in relative_parts):
            return True
    return False


def run_tests_and_get_results() -> str:
    """Запускает pytest с coverage и возвращает форматированный вывод."""
    if not has_tests():
        return "\n*Тесты пока не добавлены.*\n"

    print("\n🧪 Запуск тестов с coverage...")
    try:
        result = subprocess.run(
            ["uv", "run", "pytest", "--cov", "--cov-report=term", "--cov-report=html"],
            capture_output=True,
            text=True,
            encoding="utf-8",
            cwd=PROJECT_ROOT,
            check=False,
        )
    except FileNotFoundError:
        return "```\n⚠️ uv не найден в PATH\n```\n"

    output = result.stdout + result.stderr
    if "No module named pytest" in output or "Failed to spawn: `pytest`" in output:
        return "```\n⚠️ Pytest не установлен. Установите: uv add --group dev pytest pytest-cov\n```\n"

    lines = output.split("\n")
    coverage_lines = [line for line in lines if line.startswith("TOTAL")]
    summary_lines = [line for line in lines if line.startswith("=") and ("passed" in line or "failed" in line)]

    parts = ["### 📊 Результаты тестов\n", "```"]
    if result.returncode != 0:
        parts.append("❌ Некоторые тесты не прошли!")
    parts.extend(summary_lines or lines[-10:])
    if coverage_lines:
        parts.append(f"📈 Покрытие: {coverage_lines[-1]}")
    parts.append("```\n")
    parts.append("> 📊 **HTML отчёт покрытия**: [`htmlcov/index.html`](htmlcov/index.html)\n")
    return "\n".join(parts)


def replace_section(marker: str, body: str) -> bool:
    """Заменяет содержимое между маркерами <!-- СЕКЦИЯ_AUTO_<marker>: СТАРТ/КОНЕЦ --> в README."""
    if not README_FILE.exists():
        print(f"❌ Файл {README_FILE.name} не найден!")
        return False

    content = README_FILE.read_text(encoding="utf-8")
    start, end = f"<!-- СЕКЦИЯ_AUTO_{marker}: СТАРТ -->", f"<!-- СЕКЦИЯ_AUTO_{marker}: КОНЕЦ -->"
    pattern = re.compile(re.escape(start) + r".*?" + re.escape(end), re.DOTALL)
    new_section = f"{start}\n{body}\n{end}"

    if pattern.search(content):
        # lambda, чтобы re.sub не интерпретировал обратные слеши в тексте
        content = pattern.sub(lambda _: new_section, content, count=1)
        print(f"✅ Обновлена секция {marker}")
    else:
        content = content.rstrip() + "\n\n" + new_section + "\n"
        print(f"⚠️ Маркеры {marker} не найдены, секция добавлена в конец README")

    README_FILE.write_text(content, encoding="utf-8")
    return True


def details(summary: str, body: str) -> str:
    """Оборачивает блок в сворачиваемый <details>."""
    return f"<details>\n<summary>{summary}</summary>\n\n{body}\n\n</details>"


def main() -> None:
    """Собирает docstring, обновляет секции README и подробную документацию."""
    print("=" * 50)
    print("🔍 Генератор документации README из docstring")
    print("=" * 50)

    py_files = find_python_files()
    print(f"📁 Найдено Python-файлов: {len(py_files)}")
    if not py_files:
        print("❌ Нет Python-файлов для обработки!")
        return

    all_docs: list[dict[str, Any]] = []
    for py_file in py_files:
        docs = extract_docstrings_from_file(py_file)
        if docs:
            print(f"  ✓ {py_file.relative_to(PROJECT_ROOT).as_posix()}: {len(docs)} элементов")
            all_docs.extend(docs)
    print(f"\n📊 Всего документировано: {len(all_docs)} элементов")

    docs_path = DOCS_OUTPUT_DIR.as_posix()
    api_body = "\n".join(
        [
            "*Этот раздел генерируется автоматически из docstring.*\n",
            "| Модуль | Функция/Класс | Краткое описание |",
            "|--------|---------------|------------------|",
            generate_api_table(all_docs),
            f"\n> 📘 **Полная документация** доступна в папке [`{docs_path}`]({docs_path}).",
        ]
    )
    replace_section("API", details("📚 Документация API (развёрнуть)", api_body))

    count = generate_detailed_docs(all_docs)
    print(f"✅ Создано {count} страниц документации в {docs_path}")

    structure_body = "*Этот раздел генерируется автоматически.*\n\n" + generate_project_structure()
    replace_section("STRUCTURE", details("📁 Структура проекта (развёрнуть)", structure_body))

    if "СЕКЦИЯ_AUTO_TEST" in README_FILE.read_text(encoding="utf-8") or has_tests():
        replace_section("TEST", details("📊 Результаты тестов и покрытие (развёрнуть)", run_tests_and_get_results()))

    print("\n🎉 Готово!")


if __name__ == "__main__":
    main()
