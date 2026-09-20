"""
cli.py
Консольна точка входу та оркестратор статичного аналізатора утиліт.
Розбирає аргументи командного рядка, запускає синтаксичний сканер,
класифікатор порушень, виводить звіт та повертає відповідні коди завершення.
"""

import sys
import argparse
from pathlib import Path
from typing import List, Optional

from ast_scanner import AstScanner
from classifier import UtilityClassifier
from reporter import ReportFormatter
from sample_codebase import get_sample_sources, create_sample_files


class CliApplication:
    """Консольний контролер статичного аудитора кодової бази."""

    def __init__(self):
        self.scanner = AstScanner()

    def create_parser(self) -> argparse.ArgumentParser:
        """Створює парсер аргументів командного рядка."""
        parser = argparse.ArgumentParser(
            description="Статичний аналізатор спільних утиліт (utils) для виявлення деградації коду."
        )
        parser.add_argument(
            "--utils-dir",
            type=str,
            help="Шлях до каталогу або файла зі спільними утилітами.",
        )
        parser.add_argument(
            "--client-dir",
            type=str,
            action="append",
            help="Шлях до каталогу або файла клієнтських модулів (можна вказувати декілька разів).",
        )
        parser.add_argument(
            "--domain-types",
            type=str,
            default="Order,User,Payment,Invoice",
            help="Список доменних типів через кому для виявлення витоків бізнес-логіки.",
        )
        parser.add_argument(
            "--format",
            choices=["text", "json"],
            default="text",
            help="Формат підсумкового звіту (text або json).",
        )
        parser.add_argument(
            "--output",
            type=str,
            help="Шлях до файла для збереження звіту.",
        )
        parser.add_argument(
            "--demo",
            action="store_true",
            help="Запустити аналіз на вбудованій синтетичній кодовій базі.",
        )
        return parser

    def _collect_py_files(self, paths: List[str]) -> List[str]:
        """Рекурсивно знаходить усі `.py` файли за наданими шляхами."""
        collected = []
        for p_str in paths:
            p = Path(p_str)
            if p.is_file() and p.suffix == ".py":
                collected.append(str(p))
            elif p.is_dir():
                for py_file in p.glob("**/*.py"):
                    collected.append(str(py_file))
        return sorted(list(set(collected)))

    def run(self, args: Optional[List[str]] = None) -> int:
        """
        Запускає конвеєр статичного аналізу.
        Повертає нормативний код виходу:
          0 — чиста кодова база без аномалій,
          1 — виявлено архітектурні порушення,
          2 — помилка конфігурації або синтаксису.
        """
        if hasattr(sys.stdout, "reconfigure"):
            sys.stdout.reconfigure(encoding="utf-8")

        parser = self.create_parser()
        try:
            parsed_args = parser.parse_args(args)
        except SystemExit as exc:
            return 2 if exc.code != 0 else 0

        domain_types = [
            dt.strip() for dt in parsed_args.domain_types.split(",") if dt.strip()
        ]

        if parsed_args.demo:
            utils_sources, client_sources, demo_domain_types = get_sample_sources()
            if not parsed_args.domain_types or parsed_args.domain_types == "Order,User,Payment,Invoice":
                domain_types = demo_domain_types

            functions = self.scanner.scan_utility_sources(utils_sources)
            target_func_names = {f.name for f in functions}
            calls = self.scanner.scan_client_sources(client_sources, target_func_names)

        else:
            if not parsed_args.utils_dir:
                print(
                    "Помилка конфігурації: Вкажіть --utils-dir або використайте прапорець --demo.",
                    file=sys.stderr,
                )
                return 2

            utils_path = Path(parsed_args.utils_dir)
            if not utils_path.exists():
                print(
                    f"Помилка: Вказаний шлях утиліт '{parsed_args.utils_dir}' не існує.",
                    file=sys.stderr,
                )
                return 2

            utils_files = self._collect_py_files([parsed_args.utils_dir])
            if not utils_files:
                print(
                    f"Помилка: У '{parsed_args.utils_dir}' не знайдено файлів Python.",
                    file=sys.stderr,
                )
                return 2

            client_paths = parsed_args.client_dir or []
            client_files = self._collect_py_files(client_paths)

            try:
                functions = self.scanner.scan_utility_files(utils_files)
                target_func_names = {f.name for f in functions}
                calls = self.scanner.scan_client_files(client_files, target_func_names)
            except Exception as e:
                print(f"Помилка синтаксичного аналізу: {e}", file=sys.stderr)
                return 2

        classifier = UtilityClassifier(domain_types=domain_types)
        report = classifier.classify(functions=functions, calls=calls)

        formatter = ReportFormatter()
        if parsed_args.format == "json":
            output_content = formatter.to_json(report)
        else:
            output_content = formatter.to_table(report)

        if parsed_args.output:
            try:
                Path(parsed_args.output).write_text(output_content, encoding="utf-8")
                print(f"Звіт успішно збережено у файл: {parsed_args.output}")
            except Exception as e:
                print(f"Помилка запису файлу звіту: {e}", file=sys.stderr)
                return 2
        else:
            print(output_content)

        return 0 if report.passed else 1


def main():
    app = CliApplication()
    sys.exit(app.run())


if __name__ == "__main__":
    main()
