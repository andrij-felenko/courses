"""
reporter.py
Форматувальник результатів статичного аналізу кодової бази.
Відповідає за вивід у форматі JSON та консольної підсумкової таблиці.
"""

import json
from models import AuditReport


class ReportFormatter:
    """Генератор машиночитаних та текстових звітів про стан утиліт."""

    def to_json(self, report: AuditReport, indent: int = 2) -> str:
        """Повертає підсумковий звіт у форматі JSON."""
        return json.dumps(report.to_dict(), ensure_ascii=False, indent=indent)

    def to_table(self, report: AuditReport) -> str:
        """Повертає форматовану текстову таблицю з деталізацією знахідок та рекомендацій."""
        lines = []
        lines.append("=" * 100)
        lines.append("                  ЗВІТ АУДИТУ СПІЛЬНИХ МОДУЛІВ УТИЛІТ (SHARED UTILS)")
        lines.append("=" * 100)

        status_str = "ПРОЙДЕНО (ЧИСТА КОДОВА БАЗА)" if report.passed else "ПОМИЛКА (ВИЯВЛЕНО АНОМАЛІЇ)"
        lines.append(f"Статус аналізу: {status_str}")
        lines.append(f"Загальна кількість аналізованих утиліт: {report.total_utilities}")
        lines.append("Розподіл за категоріями:")
        for cat_name, count in report.category_stats.items():
            lines.append(f"  * {cat_name}: {count}")
        lines.append("-" * 100)

        lines.append(
            f"{'Функція':<26} | {'Категорія':<16} | {'Ca':<3} | {'Клієнти':<22} | {'Файл:рядок':<22}"
        )
        lines.append("-" * 100)

        for f in report.findings:
            clients_str = ", ".join(f.clients) if f.clients else "немає"
            if len(clients_str) > 22:
                clients_str = clients_str[:19] + "..."

            file_loc = f"{f.file_path}:{f.line_number}"
            if len(file_loc) > 22:
                file_loc = file_loc[:19] + "..."

            lines.append(
                f"{f.function_name:<26} | {f.category.value:<16} | {f.ca_score:<3} | {clients_str:<22} | {file_loc:<22}"
            )
            lines.append(f"  [Рекомендація]: {f.recommendation}")
            lines.append("-" * 100)

        return "\n".join(lines)
