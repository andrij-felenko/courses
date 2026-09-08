"""
Модуль побудови структурованого Markdown-звіту мутаційного аудиту для коментаря до пул-реквесту.
"""

from mutmut_runner import MutantRecord, MutantStatus
from quality_gate import QualityGateResult


class MarkdownReportGenerator:
    """
    Генератор детального аналітичного Markdown-звіту для розробників та аудиторів замовника.
    """

    def generate_report(
        self,
        gate_result: QualityGateResult,
        mutants: list[MutantRecord],
        pr_identifier: str = "PR #42"
    ) -> str:
        """
        Формує повний Markdown-документ із діагностикою якості тестування.
        """
        lines: list[str] = []

        # Заголовок та статус
        lines.append("## Mutation Quality Gate: Результат приймання робіт")
        lines.append("")

        if gate_result.passed:
            lines.append(f"> **СТАТУС: СХВАЛЕНО (PASSED)** для {pr_identifier}")
            lines.append("> Усі синтетичні дефекти у зміненому коді були успішно знешкоджені тестами.")
        else:
            lines.append(f"> **СТАТУС: ВІДХИЛЕНО (FAILED)** для {pr_identifier}")
            lines.append("> Тести підрядника містять прогалини та не здатні виявити критичні логічні мутації.")

        lines.append("")
        lines.append("### Підсумкові метрики аудиту")
        lines.append("")
        lines.append("| Показник | Значення | Нормативний поріг |")
        lines.append("| :--- | :--- | :--- |")
        lines.append(f"| Загальна кількість мутантів | {gate_result.total_mutants} | - |")
        lines.append(f"| Знищено тестами (Killed) | {gate_result.killed} | - |")
        lines.append(f"| Вижило (Survived) | {gate_result.survived} | 0 |")
        lines.append(f"| Таймаути (Timeout) | {gate_result.timeout} | 0 |")
        lines.append(f"| Мутаційне покриття (Mutation Score) | {gate_result.score:.1f}% | >= {gate_result.threshold:.1f}% |")
        lines.append("")

        if not gate_result.passed and len(gate_result.reasons) > 0:
            lines.append("### Причини блокування приймання:")
            for reason in gate_result.reasons:
                lines.append(f"- {reason}")
            lines.append("")

        # Деталізація мутантів, що вижили
        survived_mutants = [m for m in mutants if m.status == MutantStatus.SURVIVED]
        if len(survived_mutants) > 0:
            lines.append("### Деталізація мутантів, що вижили")
            lines.append("")
            lines.append("Наведені нижче мутації змінили логіку програми, проте всі тести підрядника пройшли успішно.")
            lines.append("Це свідчить про відсутність перевірок граничних умов або фіктивні тести (assert-free):")
            lines.append("")

            for m in survived_mutants:
                lines.append(f"#### Мутант #{m.id}: `{m.file_path}` (рядок {m.line_number})")
                lines.append(f"- **Цільова функція:** `{m.function_name}`")
                lines.append(f"- **Опис мутації:** {m.description}")
                lines.append("- **Кодовий диф мутації:**")
                lines.append("```diff")
                lines.append(f"- {m.original_code}")
                lines.append(f"+ {m.mutated_code}")
                lines.append("```")
                lines.append("")

            lines.append("### Рекомендації для підрядника:")
            lines.append("1. Додати тестові сценарії у pytest, що перевіряють граничні значення та крайні випадки.")
            lines.append("2. Переконатися у наявності чітких перевірок `assert` для всіх можливих гілок розгалуження.")
            lines.append("3. Повторно запустити мутаційний гейт локально до отримання 100% знищення мутантів.")
            lines.append("")

        return chr(10).join(lines)
