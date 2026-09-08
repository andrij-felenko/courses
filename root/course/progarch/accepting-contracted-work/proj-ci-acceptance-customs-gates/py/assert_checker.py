"""
Модуль синтаксичної перевірки повноти тверджень (assert) у тестових сьютах.
Виявляє фіктивні тести без перевірок, тривіальні заглушки та ковтання помилок.
"""

import ast
import os
from pathlib import Path
from typing import Optional

from models import CheckResult, Severity, Violation


class AssertionInspector(ast.NodeVisitor):
    """
    Аналізатор тіла тестових функцій для виявлення фіктивного тестування.
    """

    def __init__(self, file_path: str):
        self.file_path = file_path
        self.violations: list[Violation] = []

    def is_test_function(self, node: ast.FunctionDef | ast.AsyncFunctionDef) -> bool:
        """Визначає, чи є функція тестовою за загальноприйнятими конвенціями pytest / unittest."""
        name = node.name.lower()
        return name.startswith("test_") or name.endswith("_test")

    def is_trivial_assert(self, test_expr: ast.AST) -> bool:
        """Виявляє тривіальні беззмістовні твердження: assert True, assert 1 == 1 тощо."""
        if isinstance(test_expr, ast.Constant):
            if bool(test_expr.value) is True:
                return True
        elif isinstance(test_expr, ast.Compare):
            if (
                len(test_expr.ops) == 1
                and isinstance(test_expr.ops[0], ast.Eq)
                and len(test_expr.comparators) == 1
            ):
                left = test_expr.left
                right = test_expr.comparators[0]
                if isinstance(left, ast.Constant) and isinstance(right, ast.Constant):
                    if left.value == right.value:
                        return True
        return False

    def check_test_body(self, node: ast.FunctionDef | ast.AsyncFunctionDef) -> None:
        """Перевіряє наповненість та якість тверджень усередині тестової функції."""
        assert_count = 0
        has_trivial_assert = False
        has_swallowed_exceptions = False

        for child in ast.walk(node):
            if isinstance(child, ast.Assert):
                assert_count += 1
                if self.is_trivial_assert(child.test):
                    has_trivial_assert = True

            elif isinstance(child, ast.Call):
                func = child.func
                if isinstance(func, ast.Attribute) and func.attr in {
                    "raises", "assertEqual", "assertTrue", "assertFalse", "assertIn", "assertIsNone"
                }:
                    assert_count += 1

            elif isinstance(child, ast.Try):
                for handler in child.handlers:
                    if len(handler.body) == 1 and isinstance(handler.body[0], ast.Pass):
                        has_swallowed_exceptions = True

        if assert_count == 0:
            self.violations.append(
                Violation(
                    rule_name="ZeroAssertionTestViolation",
                    file_path=self.file_path,
                    line_number=node.lineno,
                    message=(
                        f"Тестова функція '{node.name}' не містить жодного оператора 'assert' "
                        f"або виклику перевірки. Тест дає фіктивне покриття рядків."
                    ),
                    severity=Severity.ERROR
                )
            )

        if has_trivial_assert:
            self.violations.append(
                Violation(
                    rule_name="TrivialAssertionViolation",
                    file_path=self.file_path,
                    line_number=node.lineno,
                    message=(
                        f"У тестовій функції '{node.name}' виявлено тривіальний 'assert True' / "
                        f"'assert 1 == 1', який штучно імітує проходження тесту."
                    ),
                    severity=Severity.ERROR
                )
            )

        if has_swallowed_exceptions:
            self.violations.append(
                Violation(
                    rule_name="SwallowedExceptionWarning",
                    file_path=self.file_path,
                    line_number=node.lineno,
                    message=(
                        f"У тестовій функції '{node.name}' виявлено порожній блок 'except: pass', "
                        f"що маскує неочікувані помилки виконання підрядника."
                    ),
                    severity=Severity.WARNING
                )
            )

    def visit_FunctionDef(self, node: ast.FunctionDef) -> None:
        if self.is_test_function(node):
            self.check_test_body(node)
        self.generic_visit(node)

    def visit_AsyncFunctionDef(self, node: ast.AsyncFunctionDef) -> None:
        if self.is_test_function(node):
            self.check_test_body(node)
        self.generic_visit(node)


class TestAssertionChecker:
    """
    Сканер тестових файлів на повноту та коректність тестових тверджень.
    """

    def __init__(self, tests_dir: str = "tests"):
        self.tests_dir = Path(tests_dir)

    def find_test_files(self) -> list[Path]:
        """Знаходить усі файли тестів у цільовому каталозі."""
        if not self.tests_dir.exists():
            return []
        test_files = []
        for root, _, files in os.walk(self.tests_dir):
            for f in files:
                if (f.startswith("test_") or f.endswith("_test.py")) and f.endswith(".py"):
                    test_files.append(Path(root) / f)
        return test_files

    def check_file(self, file_path: Path) -> list[Violation]:
        """Парсить AST файлу та повертає виявлені дефекти перевірок."""
        try:
            with open(file_path, "r", encoding="utf-8") as f:
                source = f.read()
            tree = ast.parse(source, filename=str(file_path))
        except (SyntaxError, UnicodeDecodeError) as err:
            return [
                Violation(
                    rule_name="TestSyntaxError",
                    file_path=str(file_path),
                    line_number=1,
                    message=f"Неможливо розібрати синтаксис тестового файлу: {err}",
                    severity=Severity.ERROR
                )
            ]

        inspector = AssertionInspector(str(file_path))
        inspector.visit(tree)
        return inspector.violations

    def run(self, explicit_files: Optional[list[Path]] = None) -> CheckResult:
        """Запускає аудит тестових наборів."""
        files = explicit_files if explicit_files is not None else self.find_test_files()
        all_violations: list[Violation] = []

        for f in files:
            all_violations.extend(self.check_file(f))

        passed = all(v.severity != Severity.ERROR for v in all_violations)
        summary = (
            f"Проскановано тестових файлів: {len(files)}. "
            f"Критичних дефектів тестів: {sum(1 for v in all_violations if v.severity == Severity.ERROR)}, "
            f"Застережень: {sum(1 for v in all_violations if v.severity == Severity.WARNING)}."
        )
        return CheckResult(
            check_name="TestAssertionCompletenessCheck",
            passed=passed,
            violations=all_violations,
            summary=summary
        )
