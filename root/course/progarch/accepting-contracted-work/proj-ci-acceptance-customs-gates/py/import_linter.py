"""
Модуль синтаксичної перевірки архітектурних інваріантів графа імпортів.
Використовує модуль ast для контролю міжшарової ізоляції коду підрядника.
"""

import ast
import os
from pathlib import Path
from typing import Optional

from models import CheckResult, LayerRule, Severity, Violation


class ImportGraphLinter:
    """
    Валідатор імпортів кодової бази на відповідність архітектурному шаруванню.
    """

    def __init__(self, rules: Optional[list[LayerRule]] = None, root_dir: str = "."):
        self.root_dir = Path(root_dir)
        # Типові архітектурні інваріанти чистої архітектури (Clean Architecture / DDD)
        if rules is None:
            self.rules = [
                # Доменний шар ніколи не повинен залежати від інфраструктури, веб-контролерів чи API
                LayerRule(
                    source_layer="domain",
                    forbidden_targets=["infrastructure", "interfaces", "web", "api", "controllers"]
                ),
                # Шар застосунку (use-cases) не повинен залежати від конкретних реалізацій інфраструктури
                LayerRule(
                    source_layer="application",
                    forbidden_targets=["infrastructure", "web", "controllers"]
                ),
            ]
        else:
            self.rules = rules

    def find_py_files(self, target_dir: Optional[Path] = None) -> list[Path]:
        """Рекурсивно знаходить усі цільові .py файли проєкту, ігноруючи віртуальні оточення."""
        base = target_dir if target_dir else self.root_dir
        py_files = []
        for root, dirs, files in os.walk(base):
            # Пропускаємо службові каталоги
            dirs[:] = [d for d in dirs if d not in {".git", ".venv", "venv", "__pycache__", ".pytest_cache"}]
            for f in files:
                if f.endswith(".py"):
                    py_files.append(Path(root) / f)
        return py_files

    def extract_imports(self, file_path: Path) -> list[tuple[int, str]]:
        """
        Парсить AST файлу та повертає список кортежів: (номер рядка, імпортований модуль).
        """
        try:
            with open(file_path, "r", encoding="utf-8") as f:
                source = f.read()
            tree = ast.parse(source, filename=str(file_path))
        except (SyntaxError, UnicodeDecodeError) as err:
            return [(1, f"<syntax_error: {err}>")]

        imports: list[tuple[int, str]] = []
        for node in ast.walk(tree):
            if isinstance(node, ast.Import):
                for alias in node.names:
                    imports.append((node.lineno, alias.name))
            elif isinstance(node, ast.ImportFrom):
                module = node.module or ""
                for alias in node.names:
                    full_name = f"{module}.{alias.name}" if module else alias.name
                    imports.append((node.lineno, full_name))
        return imports

    def detect_layer(self, file_path: Path) -> Optional[str]:
        """Визначає приналежність файлу до архітектурного шару за його розташуванням у шляху."""
        rel_str = str(file_path.resolve()).replace("\\", "/").lower()
        parts = rel_str.split("/")
        for rule in self.rules:
            if rule.source_layer.lower() in parts:
                return rule.source_layer
        return None

    def check_file(self, file_path: Path) -> list[Violation]:
        """Перевіряє одиничний файл на наявність заборонених імпортів."""
        layer = self.detect_layer(file_path)
        if not layer:
            return []

        active_rules = [r for r in self.rules if r.source_layer == layer]
        if not active_rules:
            return []

        violations: list[Violation] = []
        imports = self.extract_imports(file_path)

        for lineno, imp_target in imports:
            imp_parts = imp_target.lower().split(".")
            for rule in active_rules:
                for forbidden in rule.forbidden_targets:
                    if forbidden.lower() in imp_parts:
                        violations.append(
                            Violation(
                                rule_name="ArchitectureLayerViolation",
                                file_path=str(file_path),
                                line_number=lineno,
                                message=(
                                    f"Порушення архітектурного шару '{layer}': заборонено імпортувати "
                                    f"модуль '{imp_target}' (цільовий шар '{forbidden}')."
                                ),
                                severity=Severity.ERROR
                            )
                        )
        return violations

    def run(self) -> CheckResult:
        """Виконує повний аудит графа імпортів у кодовій базі."""
        all_violations: list[Violation] = []
        files = self.find_py_files()

        for f in files:
            all_violations.extend(self.check_file(f))

        passed = len(all_violations) == 0
        summary = (
            f"Перевірено файлів: {len(files)}. Порушень шарування: {len(all_violations)}."
        )
        return CheckResult(
            check_name="ArchitecturalImportsCheck",
            passed=passed,
            violations=all_violations,
            summary=summary
        )
