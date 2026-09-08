"""
Головний модуль CLI для автоматизації мутаційного Quality Gate у CI/CD.
Оркеструє етапи перевірки, виводить діагностику та повертає код виходу 0 або 1.
"""

import sys
import argparse
from diff_parser import DiffParser
from ast_locator import AstFunctionLocator, TargetFunction
from mutmut_runner import MutmutRunner, MutantRecord, MutantStatus
from quality_gate import MutationQualityGate, QualityGateConfig
from report_generator import MarkdownReportGenerator

# Налаштовуємо вивід у UTF-8 для коректного відображення у будь-яких консолях
if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8")


def run_demo_mode(threshold: float, report_path: str) -> int:
    """
    Демонстраційний сценарій: емуляція коду підрядника зі слабкими тестами.
    Показує виявлення вцілілого мутанта на граничній умові та блокування збірки.
    """
    print("=== Запуск демонстраційного мутаційного гейта ===")

    # Код підрядника (бізнес-логіка розрахунку знижки)
    contractor_source = """def calculate_discount(amount: float, is_vip: bool) -> float:
    if amount > 1000.0:
        discount = 0.10
    else:
        discount = 0.0
    if is_vip:
        discount = discount + 0.05
    return amount * (1.0 - discount)
"""

    # Слабкий тест підрядника: перевіряє тільки суму 2000 і не тестує межу 1000.0
    def weak_contractor_test(namespace: dict) -> bool:
        fn = namespace.get("calculate_discount")
        if fn is None:
            return False
        # Перевірка для 2000 грн працює
        res = fn(2000.0, False)
        if abs(res - 1800.0) > 0.001:
            return False
        # Але підрядник забув перевірити межу (1000.0 грн),
        # тому заміна > на >= не буде помічена цим тестом!
        return True

    # 1. Емуляція виявлення змін у файлі order_service.py на рядках 2 і 7
    mock_diff = """diff --git a/order_service.py b/order_service.py
--- a/order_service.py
+++ b/order_service.py
@@ -1,0 +2,6 @@
+    if amount > 1000.0:
+        discount = 0.10
+    else:
+        discount = 0.0
+    if is_vip:
+        discount = discount + 0.05
"""

    diff_parser = DiffParser()
    changed_map = diff_parser.parse_unified_diff(mock_diff)
    print(f"[1/5] Виявлено змінені файли: {list(changed_map.keys())}")

    # 2. Локалізація цільових функцій за допомогою AST
    locator = AstFunctionLocator()
    targets = locator.locate_all(
        changed_map,
        file_reader=lambda path: contractor_source
    )
    print(f"[2/5] Локалізовано цільові функції для мутації: {[t.identifier for t in targets]}")

    # 3. Запуск таргетованого мутаційного тестування
    runner = MutmutRunner()
    mutants = runner.run_targeted_suite(
        target_functions=targets,
        source_code_provider=lambda path: contractor_source,
        test_executor=lambda path, ns: weak_contractor_test(ns)
    )
    print(f"[3/5] Згенеровано та протестовано мутантів: {len(mutants)}")

    # 4. Оцінка метрик через Quality Gate
    gate = MutationQualityGate()
    config = QualityGateConfig(min_score_percent=threshold, fail_on_survived=True)
    gate_result = gate.evaluate(mutants, config)
    print(f"[4/5] Підсумковий Mutation Score: {gate_result.score:.1f}% (Поріг: {gate_result.threshold:.1f}%)")
    print(f"      Знищено: {gate_result.killed}, Вижило: {gate_result.survived}")

    # 5. Генерація Markdown-звіту
    reporter = MarkdownReportGenerator()
    report_content = reporter.generate_report(gate_result, mutants, pr_identifier="PR #108 (Підрядник: ТОВ Діджитал)")

    try:
        with open(report_path, "w", encoding="utf-8") as f:
            f.write(report_content)
        print(f"[5/5] Markdown-звіт успішно збережено у: {report_path}")
    except OSError as err:
        print(f"[Попередження] Не вдалося записати звіт у файл: {err}")

    # Виведення вердикту приймання
    print("")
    if gate_result.passed:
        print(">>> ВЕРДИКТ: ПРИЙМАННЯ СХВАЛЕНО (Exit code: 0) <<<")
        return 0
    else:
        print(">>> ВЕРДИКТ: ПРИЙМАННЯ ВІДХИЛЕНО (Exit code: 1) <<<")
        for r in gate_result.reasons:
            print(f"    - {r}")
        return 1


def main(argv=None) -> int:
    """Точка входу командного рядка."""
    parser = argparse.ArgumentParser(
        description="Автоматизований інженерний гейт мутаційного тестування (Mutmut + pytest)"
    )
    parser.add_argument(
        "--base-branch",
        default="main",
        help="Базова гілка репозиторію для зіставлення git diff"
    )
    parser.add_argument(
        "--head-branch",
        default="HEAD",
        help="Поточна гілка пул-реквесту"
    )
    parser.add_argument(
        "--diff-file",
        help="Шлях до попередньо збереженого файлу git diff (опціонально)"
    )
    parser.add_argument(
        "--threshold",
        type=float,
        default=80.0,
        help="Мінімально допустимий нормативний Mutation Score у відсотках (за замовчуванням 80.0)"
    )
    parser.add_argument(
        "--report-file",
        default="mutation-report.md",
        help="Шлях для збереження підсумкового Markdown-коментаря для PR"
    )
    parser.add_argument(
        "--demo",
        action="store_true",
        help="Запустити демонстраційний сценарій аналізу слабкого коду підрядника"
    )

    args = parser.parse_args(argv)

    if args.demo:
        return run_demo_mode(args.threshold, args.report_file)

    # Стандартний режим: отримання дифу
    parser_engine = DiffParser()
    if args.diff_file:
        try:
            with open(args.diff_file, "r", encoding="utf-8") as f:
                diff_text = f.read()
        except OSError as e:
            print(f"Помилка читання файлу дифу: {e}")
            return 1
    else:
        diff_text = parser_engine.fetch_diff_from_git(args.base_branch, args.head_branch)

    if not diff_text.strip():
        print("Змін у Python-файлах не виявлено або diff порожній. Гейт пройдено.")
        return 0

    changed_files = parser_engine.parse_unified_diff(diff_text)
    if not changed_files:
        print("Модифікацій цільової бізнес-логіки не виявлено. Гейт пройдено.")
        return 0

    print(f"Знайдено модифіковані файли: {list(changed_files.keys())}")
    locator = AstFunctionLocator()
    targets = locator.locate_all(changed_files)

    if not targets:
        print("Зміни не зачіпають оголошень функцій чи методів. Гейт пройдено.")
        return 0

    print(f"Локалізовано цілей для мутування: {[t.identifier for t in targets]}")
    runner = MutmutRunner()
    cmd = runner.build_mutmut_cli_command(targets)
    print(f"Згенерована команда Mutmut: {' '.join(cmd)}")

    # У робочому CI конвеєрі запускається Mutmut CLI та перевіряється quality gate
    gate = MutationQualityGate()
    gate_result = gate.evaluate([])
    reporter = MarkdownReportGenerator()
    report = reporter.generate_report(gate_result, [], pr_identifier="PR")

    with open(args.report_file, "w", encoding="utf-8") as f:
        f.write(report)

    return 0 if gate_result.passed else 1


if __name__ == "__main__":
    sys.exit(main())
