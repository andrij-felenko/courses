"""
report_generator.py — Генератор звітів аудиту передачі системи (Clean-Slate Audit Report).
Створює машиночитаний JSON для пайплайнів CI та структурований Markdown для інженерів.
"""

from dataclasses import dataclass, field, asdict
from datetime import datetime
from pathlib import Path
import json
from typing import Any


@dataclass
class PhaseReport:
    """Звіт окремої фази валідації розгортання."""

    phase_id: str
    name: str
    passed: bool
    duration_sec: float
    summary: str
    details: dict[str, Any] = field(default_factory=dict)


@dataclass
class AuditReport:
    """Зведений фінальний звіт передачі кодової бази."""

    project_name: str
    passed: bool
    started_at: str
    total_duration_sec: float
    phases: list[PhaseReport]
    metadata: dict[str, str] = field(default_factory=dict)


class AuditReporter:
    """
    Агрегатор результатів перевірки системи та генератор звітів для CI Quality Gate.
    """

    def __init__(self, project_name: str = "TargetSystem") -> None:
        self.project_name = project_name
        self.started_at = datetime.now().isoformat()
        self.phases: list[PhaseReport] = []
        self.metadata: dict[str, str] = {}

    def add_phase(
        self,
        phase_id: str,
        name: str,
        passed: bool,
        duration_sec: float,
        summary: str,
        details: dict[str, Any] | None = None,
    ) -> None:
        """Додає зафіксовані результати фази аудиту."""
        self.phases.append(
            PhaseReport(
                phase_id=phase_id,
                name=name,
                passed=passed,
                duration_sec=round(duration_sec, 3),
                summary=summary,
                details=details or {},
            )
        )

    def build_report(self, total_duration_sec: float) -> AuditReport:
        """Формує підсумковий об'єкт аудиту."""
        all_passed = all(p.passed for p in self.phases)
        return AuditReport(
            project_name=self.project_name,
            passed=all_passed,
            started_at=self.started_at,
            total_duration_sec=round(total_duration_sec, 3),
            phases=self.phases,
            metadata=self.metadata,
        )

    def to_json(self, total_duration_sec: float, indent: int = 2) -> str:
        """Генерує машиночитаний JSON-звіт для автоматизованих перевірок у CI/CD."""
        report = self.build_report(total_duration_sec)
        return json.dumps(asdict(report), ensure_ascii=False, indent=indent)

    def to_markdown(self, total_duration_sec: float) -> str:
        """
        Генерує структурований звіт у форматі Markdown із таблицями статусів та алертами.
        """
        report = self.build_report(total_duration_sec)
        status_badge = "[PASS] ГОТОВО ДО ПЕРЕДАЧІ" if report.passed else "[FAIL] ПЕРЕДАЧА ЗАБЛОКОВАНА"

        lines: list[str] = [
            f"# Звіт аудиту розгортання «із чистого аркуша»: {report.project_name}",
            "",
            f"**Статус аудиту**: `{status_badge}`  ",
            f"**Час запуску**: `{report.started_at}`  ",
            f"**Загальна тривалість**: `{report.total_duration_sec} с`  ",
            "",
        ]

        if report.passed:
            lines.extend([
                "> [!IMPORTANT]",
                "> Систему успішно верифіковано: конфігурація не містить витоків локального середовища,",
                "> база даних повністю ідемпотентна (up-down-up), а сервіс успішно підіймається «холодним стартом».",
                "",
            ])
        else:
            lines.extend([
                "> [!WARNING]",
                "> Виявлено дефекти автономного розгортання! Систему не можна передавати іншій команді",
                "> без виправлення зафіксованих блокуючих зауважень нижче.",
                "",
            ])

        lines.extend([
            "## Зведена таблиця фаз валідації",
            "",
            "| Фаза | Статус | Тривалість | Результат |",
            "| :--- | :---: | :---: | :--- |",
        ])

        for p in report.phases:
            p_status = "[PASS]" if p.passed else "[FAIL]"
            lines.append(f"| {p.name} | **{p_status}** | {p.duration_sec} с | {p.summary} |")

        lines.append("")
        lines.append("## Детальний аналіз фаз")
        lines.append("")

        for p in report.phases:
            lines.append(f"### {p.name}")
            lines.append(f"- **Підсумок**: {p.summary}")
            lines.append(f"- **Тривалість**: {p.duration_sec} секунд")

            if p.details.get("missing_env_vars"):
                lines.append("- **Відсутні змінні оточення**:")
                for m in p.details["missing_env_vars"]:
                    lines.append(f"  - `{m}`")

            if p.details.get("violations"):
                lines.append("- **Виявлені витоки локальних шляхів**:")
                for v in p.details["violations"]:
                    lines.append(f"  - `{v['file_path']}:{v['line_number']}`: {v['message']}")

            if p.details.get("errors"):
                lines.append("- **Зафіксовані помилки**:")
                for err in p.details["errors"]:
                    lines.append(f"  - [ПОМИЛКА] {err}")

            lines.append("")

        return "\n".join(lines)

    def save(
        self, target_dir: Path, total_duration_sec: float, base_name: str = "clean_slate_report"
    ) -> tuple[Path, Path]:
        """Зберігає звіти у форматах .json та .md у вказану директорію."""
        target_dir.mkdir(parents=True, exist_ok=True)
        json_path = target_dir / f"{base_name}.json"
        md_path = target_dir / f"{base_name}.md"

        json_path.write_text(self.to_json(total_duration_sec), encoding="utf-8")
        md_path.write_text(self.to_markdown(total_duration_sec), encoding="utf-8")

        return json_path, md_path
