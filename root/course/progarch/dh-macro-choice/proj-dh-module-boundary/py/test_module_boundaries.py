# tests/architecture/test_module_boundaries.py
import ast
import os
import pytest

MODULES_ROOT_PATH = os.path.abspath("cloud-core/modules")

def find_all_python_files(directory: str):
    """Рекурсивний пошук усіх Python-файлів у каталозі модулів."""
    for root, _, files in os.walk(directory):
        for file in files:
            if file.endswith(".py"):
                yield os.path.join(root, file)

def inspect_file_imports(file_path: str, current_module_name: str) -> list[str]:
    """Аналізує синтаксичне дерево (AST) файлу та виявляє несанкціоновані імпорти."""
    with open(file_path, "r", encoding="utf-8") as file_handle:
        try:
            tree = ast.parse(file_handle.read(), filename=file_path)
        except SyntaxError as err:
            return [f"Синтаксична помилка у файлі {file_path}: {err}"]

    violations = []
    for node in ast.walk(tree):
        imported_module_path = None
        
        # Обробка конструкцій вида 'import modules.billing.internal.models'
        if isinstance(node, ast.Import):
            for alias in node.names:
                imported_module_path = alias.name
        # Обробка конструкцій вида 'from modules.billing.internal.models import Invoice'
        elif isinstance(node, ast.ImportFrom):
            imported_module_path = node.module or ""

        if imported_module_path and "modules." in imported_module_path:
            path_segments = imported_module_path.split(".")
            # Очікуваний формат: ['modules', 'target_module_name', 'subpackage', ...]
            if len(path_segments) > 1:
                target_module_name = path_segments[1]

                # Перевірка 1: Заборона імпорту приватного вмісту (internal) чужого модуля
                if target_module_name != current_module_name:
                    if "internal" in path_segments:
                        violations.append(
                            f"ПОРУШЕННЯ МЕЖІ: {file_path}:{node.lineno} -> "
                            f"Модуль '{current_module_name}' імпортує приватний код '{imported_module_path}'! "
                            f"Дозволено імпортувати лише modules.{target_module_name}.contract або events."
                        )
                    elif len(path_segments) > 2 and path_segments[2] not in ("contract", "events"):
                        violations.append(
                            f"ПОРУШЕННЯ МЕЖІ: {file_path}:{node.lineno} -> "
                            f"Модуль '{current_module_name}' імпортує неприпустимий файл '{imported_module_path}'!"
                        )

    return violations

def test_enforce_strict_module_boundaries():
    """Головний архітектурний тест для CI/CD."""
    all_boundary_violations = []

    if not os.path.exists(MODULES_ROOT_PATH):
        pytest.fail(f"Каталог модулів не знайдено за шляхом: {MODULES_ROOT_PATH}")

    for entry in os.listdir(MODULES_ROOT_PATH):
        module_dir = os.path.join(MODULES_ROOT_PATH, entry)
        if os.path.isdir(module_dir):
            for py_file in find_all_python_files(module_dir):
                file_violations = inspect_file_imports(py_file, current_module_name=entry)
                all_boundary_violations.extend(file_violations)

    # Якщо виявлено хоча б одне порушення — тест виводить чіткий звіт і валить збірку
    assert not all_boundary_violations, (
        "Виявлено порушення архітектурних меж модульного моноліту:\n" +
        "\n".join(all_boundary_violations)
    )
