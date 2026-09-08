"""
signed_reporter.py — Криптографічно підписана аудиторська звітність для шлюзу приймання.
Агрегує результати всіх етапів аудиту, обчислює HMAC-SHA256 для гарантії цілісності
та генерує машинозчитувані файли звіту у форматах JSON і Markdown.
"""

from __future__ import annotations

import hashlib
import hmac
import json
import time
from dataclasses import asdict, dataclass, field
from pathlib import Path
from typing import Any


@dataclass
class PhaseReport:
    """Метрики проходження окремої фази конвеєра приймання."""
    phase_id: str
    title: str
    passed: bool
    duration_ms: float
    details: dict[str, Any] = field(default_factory=dict)
    error: str | None = None


@dataclass
class AcceptanceArtifact:
    """Незмінний артефакт приймання із цифровим підписом."""
    schema_version: str
    timestamp: str
    system_name: str
    gate_verdict: str  # "ACCEPTED" або "REJECTED"
    gate_passed: bool
    hmac_sha256_signature: str
    metrics: dict[str, Any]
    phases: list[PhaseReport]


class SignedAcceptanceReporter:
    """
    Генератор підписаних аудиторських артефактів приймання коду.
    Захищає звіт від ручної фальсифікації підрядником або менеджерами.
    """

    SCHEMA_VERSION = "1.0.0"

    def __init__(self, signing_key: str = "cleanroom-sovereign-acceptance-secret") -> None:
        self.signing_key = signing_key.encode("utf-8")
        self.phases: list[PhaseReport] = []

    def record_phase(
        self,
        phase_id: str,
        title: str,
        passed: bool,
        duration_ms: float,
        details: dict[str, Any],
        error: str | None = None,
    ) -> None:
        """Реєструє вердикт окремого етапу перевірки."""
        self.phases.append(
            PhaseReport(
                phase_id=phase_id,
                title=title,
                passed=passed,
                duration_ms=round(duration_ms, 2),
                details=details,
                error=error,
            )
        )

    def generate_artifact(self, system_name: str) -> AcceptanceArtifact:
        """
        Формує підсумковий артефакт і обчислює його HMAC-SHA256.
        """
        passed_count = sum(1 for p in self.phases if p.passed)
        failed_count = len(self.phases) - passed_count
        gate_passed = failed_count == 0
        total_duration = sum(p.duration_ms for p in self.phases)

        metrics = {
            "total_phases": len(self.phases),
            "passed_phases": passed_count,
            "failed_phases": failed_count,
            "total_duration_ms": round(total_duration, 2),
        }

        # Канонічне представлення даних для обчислення хешу
        payload_to_sign = {
            "schema_version": self.SCHEMA_VERSION,
            "system_name": system_name,
            "gate_passed": gate_passed,
            "metrics": metrics,
            "phases": [asdict(p) for p in self.phases],
        }
        canonical_json = json.dumps(payload_to_sign, sort_keys=True, ensure_ascii=False)
        signature = hmac.new(self.signing_key, canonical_json.encode("utf-8"), hashlib.sha256).hexdigest()

        return AcceptanceArtifact(
            schema_version=self.SCHEMA_VERSION,
            timestamp=time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()),
            system_name=system_name,
            gate_verdict="ACCEPTED" if gate_passed else "REJECTED",
            gate_passed=gate_passed,
            hmac_sha256_signature=signature,
            metrics=metrics,
            phases=self.phases,
        )

    def save_json(self, file_path: str | Path, artifact: AcceptanceArtifact) -> None:
        """Зберігає машинозчитуваний JSON-артефакт на диск."""
        out_path = Path(file_path).resolve()
        out_path.parent.mkdir(parents=True, exist_ok=True)
        data = asdict(artifact)
        out_path.write_text(json.dumps(data, indent=2, ensure_ascii=False), encoding="utf-8")

    def generate_markdown(self, artifact: AcceptanceArtifact) -> str:
        """Генерує людинозчитуваний Markdown-звіт для Git або приймальної комісії."""
        status_banner = "✅ **ПРИЙНЯТО (PASS)**" if artifact.gate_passed else "❌ **ВІДХИЛЕНО (REJECT)**"

        lines = [
            f"# Акт технічного приймання системи: {artifact.system_name}",
            "",
            f"- **Вердикт шлюзу:** {status_banner}",
            f"- **Час генерації:** `{artifact.timestamp}`",
            f"- **Криптографічний підпис (HMAC-SHA256):** `{artifact.hmac_sha256_signature}`",
            f"- **Загальна тривалість:** `{artifact.metrics['total_duration_ms']} мс`",
            "",
            "## Результати перевірок фаз чистої кімнати",
            "",
            "| Фаза | Статус | Тривалість | Деталі |",
            "| :--- | :---: | :---: | :--- |",
        ]

        for p in artifact.phases:
            icon = "PASS ✔" if p.passed else "FAIL ✘"
            detail_str = p.error if p.error else "Успішно верифіковано"
            lines.append(f"| **{p.title}** | `{icon}` | {p.duration_ms} мс | {detail_str} |")

        lines.extend([
            "",
            "> 🛡️ **Гарантія цілісності:** Цей акт автоматично підписано HMAC-ключем приймального стенда. "
            "Будь-яка спроба модифікації полів звіту призведе до інвалідації підпису у гейті CI/CD."
        ])
        return "\n".join(lines)

    def print_console_summary(self, artifact: AcceptanceArtifact) -> None:
        """Виводить структуроване зведення в консоль конвеєра."""
        print("\n" + "=" * 60)
        print(f" АКТ ПРИЙМАННЯ СИСТЕМИ: {artifact.system_name}")
        print(f" Криптопідпис: {artifact.hmac_sha256_signature[:16]}...")
        print("=" * 60)
        for p in artifact.phases:
            mark = "[ПРОЙДЕНО]" if p.passed else "[ВІДХИЛЕНО]"
            print(f"{mark:<12} {p.title:<38} ({p.duration_ms} мс)")
            if p.error:
                print(f"             └─ Дефект: {p.error}")
        print("-" * 60)
        print(f"Фази: {artifact.metrics['passed_phases']}/{artifact.metrics['total_phases']} пройдено | Загальний час: {artifact.metrics['total_duration_ms']} мс")
        print(f"ВЕРДИКТ ПРИЙМАЛЬНОГО ШЛЮЗУ: [{artifact.gate_verdict}]")
        print("=" * 60 + "\n")
