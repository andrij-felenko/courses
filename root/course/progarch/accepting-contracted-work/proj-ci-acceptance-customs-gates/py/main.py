"""
Головна точка входу митного контуру інженерного приймання коду (Customs Gate).
Оркеструє запуск інспекторів, зводить загальний вердикт і встановлює код повернення для CI.
"""

import sys
from pathlib import Path
from typing import Optional

# Забезпечуємо коректний вивід UTF-8 у консоль на всіх платформах
if hasattr(sys.stdout, "reconfigure"):
    try:
        sys.stdout.reconfigure(encoding="utf-8")
    except Exception:
        pass

from assert_checker import TestAssertionChecker
from import_linter import ImportGraphLinter
from license_scanner import LockfileLicenseScanner
from models import CheckResult
from pr_reporter import GitPRReporter


class CustomsGateOrchestrator:
    """
    Оркестратор митного контролю якості коду підрядника в конвеєрі CI/CD.
    """

    def __init__(self, project_root: str = "."):
        self.project_root = Path(project_root)
        self.import_linter = ImportGraphLinter(root_dir=str(self.project_root))
        self.license_scanner = LockfileLicenseScanner(
            lockfile_path=str(self.project_root / "poetry.lock")
        )
        self.assert_checker = TestAssertionChecker(
            tests_dir=str(self.project_root / "tests")
        )
        self.reporter = GitPRReporter()

    def run_pipeline(self) -> tuple[bool, list[CheckResult]]:
        """
        Виконує повну послідовність митних перевірок приймання.
        Повертає кортеж: (чи пройдено всі гейти, список результатів).
        """
        print("=" * 70)
        print("  МИНИЙ КОНТУР ПРИЙМАННЯ КОДУ ПІДРЯДНИКА (CI QUALITY GATE)")
        print("=" * 70)

        results: list[CheckResult] = []

        print("[1/3] Перевірка архітектурних інваріантів імпортів (AST)...")
        res_imports = self.import_linter.run()
        results.append(res_imports)
        print(f"      -> {res_imports.summary}")

        print("[2/3] Сканування маніфесту залежностей та перевірка ліцензій...")
        res_license = self.license_scanner.run()
        results.append(res_license)
        print(f"      -> {res_license.summary}")

        print("[3/3] Інспекція тестових тверджень (Assert Completeness)...")
        res_asserts = self.assert_checker.run()
        results.append(res_asserts)
        print(f"      -> {res_asserts.summary}")

        overall_passed = all(r.passed for r in results)

        report_md = self.reporter.generate_markdown_report(results)
        self.reporter.save_report(report_md, str(self.project_root / "customs_report.md"))
        self.reporter.post_comment_to_pr(report_md)

        print("-" * 70)
        if overall_passed:
            print("  ВЕРДИКТ: ПРИЙНЯТО! Код відповідає всім архітектурним вимогам.")
        else:
            print("  ВЕРДИКТ: ВІДХИЛЕНО! Злиття заблоковано до виправлення дефектів.")
        print("=" * 70)

        return overall_passed, results


def run_demo() -> int:
    """
    Демонстраційний режим перевірки роботи митного контуру на штучно створених сценаріях.
    Демонструє детекцію порушень архітектури, ліцензій та фіктивних тестів.
    """
    import tempfile

    with tempfile.TemporaryDirectory() as tmp_dir:
        root = Path(tmp_dir)

        domain_dir = root / "domain"
        infra_dir = root / "infrastructure"
        tests_dir = root / "tests"

        domain_dir.mkdir(parents=True)
        infra_dir.mkdir(parents=True)
        tests_dir.mkdir(parents=True)

        (infra_dir / "database.py").write_text(
            "class PostgresRepository:\n    pass\n", encoding="utf-8"
        )
        (domain_dir / "order.py").write_text(
            "from infrastructure.database import PostgresRepository  # Порушення шару!\n\n"
            "class Order:\n    def __init__(self):\n        self.repo = PostgresRepository()\n",
            encoding="utf-8"
        )

        (root / "poetry.lock").write_text(
            '[[package]]\nname = "requests"\nversion = "2.31.0"\n\n'
            '[[package]]\nname = "gpl-unapproved-driver"\nversion = "1.0.0"\nlicense = "GPL-3.0"\n',
            encoding="utf-8"
        )

        (tests_dir / "test_orders.py").write_text(
            "def test_order_creation_empty():\n"
            "    # Фіктивний тест: викликає функцію, але нічого не перевіряє\n"
            "    x = 10 + 20\n\n"
            "def test_order_trivial():\n"
            "    # Штучна імітація проходження тесту\n"
            "    assert True\n",
            encoding="utf-8"
        )

        orchestrator = CustomsGateOrchestrator(project_root=str(root))
        passed, results = orchestrator.run_pipeline()

        report_file = root / "customs_report.md"
        if report_file.exists():
            print("\n[ЗГЕНЕРОВАНИЙ ПІДСУМКОВИЙ ЗВІТ ДЛЯ PULL REQUEST]:\n")
            print(report_file.read_text(encoding="utf-8"))

        return 0 if passed else 1


def main() -> None:
    """Точка входу CLI."""
    if len(sys.argv) > 1 and sys.argv[1] != "--demo":
        target = sys.argv[1]
        orchestrator = CustomsGateOrchestrator(project_root=target)
        passed, _ = orchestrator.run_pipeline()
        sys.exit(0 if passed else 1)
    else:
        code = run_demo()
        print(f"\n[DEMO FINISHED] Код повернення гейта у реальному CI: {code} (Блокування PR).")
        sys.exit(0)


if __name__ == "__main__":
    main()
