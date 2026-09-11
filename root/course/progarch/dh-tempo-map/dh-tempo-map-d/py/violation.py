#!/usr/bin/env python3
"""
Архітектурний лінтер конвеєра CI для перевірки дотримання карти темпів.
Забороняє імпорт швидких периферійних модулів у повільне апаратне ядро.
"""

import ast
import sys
from pathlib import Path
from typing import List, NamedTuple


class Violation(NamedTuple):
    file_path: Path
    line_number: int
    imported_module: str
    reason: str


# Правила карти темпів: заборонені префікси імпортів для повільного ядра
FORBIDDEN_IMPORT_RULES = {
    # Заборона залежності ядра від швидких шарів інтерфейсу
    "digital_homes.ui": "Інверсія темпу: повільне ядро не має залежати від шару представлення (UI).",
    "digital_homes.mobile": "Інверсія темпу: прямий імпорт коду мобільного клієнта в ядро заборонено.",
    # Заборона прямої залежності ядра від мінливих зовнішніх хмарних сервісів
    "digital_homes.cloud_integrations": (
        "Порушення ізоляції: зовнішні хмарні адаптери мають підключатися "
        "через антикорупційний шар, а не імпортуватися ядром."
    ),
    # Заборона імпорту користувацьких автоматизацій
    "digital_homes.user_rules": (
        "Інверсія темпу: призначені для користувача сценарії виконуються "
        "над ядром, а не всередині нього."
    ),
}


class ImportVisitor(ast.NodeVisitor):
    def __init__(self, file_path: Path) -> None:
        self.file_path = file_path
        self.violations: List[Violation] = []

    def visit_Import(self, node: ast.Import) -> None:
        for alias in node.names:
            self._check_module_name(alias.name, node.lineno)
        self.generic_visit(node)

    def visit_ImportFrom(self, node: ast.ImportFrom) -> None:
        if node.module:
            self._check_module_name(node.module, node.lineno)
        # Перевірка спроби підключити контракти через локальний відносний шлях повз версіонований пакет
        if node.level > 0 and node.module and "contracts" in node.module:
            self.violations.append(
                Violation(
                    file_path=self.file_path,
                    line_number=node.lineno,
                    imported_module=f"{'.' * node.level}{node.module}",
                    reason=(
                        "Канонічні контракти мають імпортуватися виключно як версіонований "
                        "пакет 'dh_canonical_contracts'."
                    ),
                )
            )
        self.generic_visit(node)

    def _check_module_name(self, module_name: str, lineno: int) -> None:
        for forbidden_prefix, reason in FORBIDDEN_IMPORT_RULES.items():
            if module_name == forbidden_prefix or module_name.startswith(f"{forbidden_prefix}."):
                self.violations.append(
                    Violation(
                        file_path=self.file_path,
                        line_number=lineno,
                        imported_module=module_name,
                        reason=reason,
                    )
                )


def scan_directory(core_dir: Path) -> List[Violation]:
    all_violations: List[Violation] = []

    for python_file in core_dir.rglob("*.py"):
        try:
            tree = ast.parse(python_file.read_text(encoding="utf-8"), filename=str(python_file))
            visitor = ImportVisitor(python_file)
            visitor.visit(tree)
            all_violations.extend(visitor.violations)
        except SyntaxError as parse_err:
            all_violations.append(
                Violation(
                    file_path=python_file,
                    line_number=parse_err.lineno or 0,
                    imported_module="<помилка синтаксису>",
                    reason=f"Неможливо розібрати синтаксис файлу: {parse_err.msg}",
                )
            )

    return all_violations


def main() -> None:
    if len(sys.argv) < 2:
        print("Використання: python lint_tempo_boundaries.py <шлях_до_каталогу_core>")
        sys.exit(2)

    core_directory = Path(sys.argv[1]).resolve()
    if not core_directory.exists() or not core_directory.is_dir():
        print(f"Помилка: каталог '{core_directory}' не знайдено.")
        sys.exit(2)

    violations = scan_directory(core_directory)

    if violations:
        print(f"\n❌ Знайдено порушень карти темпів у повільному ядрі: {len(violations)}\n")
        for v in violations:
            rel_path = v.file_path.relative_to(core_directory.parent)
            print(f"  {rel_path}:{v.line_number}: імпорт '{v.imported_module}'")
            print(f"    ↳ Причина: {v.reason}\n")
        print("Збірку зупинено. Повільне ядро не може імпортувати швидку периферію.")
        sys.exit(1)

    print(f"✅ Перевірка меж карти темпів успішна: ядро '{core_directory.name}' дотримується градієнта стабільності.")
    sys.exit(0)


if __name__ == "__main__":
    main()
