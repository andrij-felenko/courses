"""
harness.py — Консольний координатор приймального стенда Clean-Room Acceptance Harness.
Запускає послідовність суворих технічних перевірок:
1. Статичний аудит офлайн-вендорингу.
2. Підйом ізольованого контейнерного контуру без доступу до Інтернету (zero-egress).
3. Верифікація двосторонньої ідемпотентності міграцій БД (up-down-up).
4. Опитування діагностичних контрактів життєздатності.
5. Генерація криптографічно підписаного артефакту приймання.
"""

from __future__ import annotations

import argparse
import sys
import time
from pathlib import Path

from container_orchestrator import CleanRoomOrchestrator
from diagnostic_client import DiagnosticClient
from migration_verifier import MigrationVerifier
from signed_reporter import SignedAcceptanceReporter
from vendoring_auditor import VendoringAuditor


class CleanRoomHarness:
    """
    Головний контролер конвеєра приймання системи від підрядника.
    """

    def __init__(
        self,
        target_dir: str | Path,
        signing_key: str = "cleanroom-sovereign-acceptance-secret",
        system_name: str = "Sovereign-Core-System",
        force_mock_containers: bool = False,
    ) -> None:
        self.target_dir = Path(target_dir).resolve()
        self.system_name = system_name
        self.force_mock_containers = force_mock_containers
        self.reporter = SignedAcceptanceReporter(signing_key=signing_key)
        self.orchestrator = CleanRoomOrchestrator()

    def run_all_acceptance_gates(self) -> bool:
        """
        Запускає всі фази аудиту в ізольованому контурі.
        Повертає True, якщо всі критерії приймання виконані.
        """
        try:
            # 1. Фаза 1: Аудит вендорингу та офлайн-архівів
            t0 = time.perf_counter()
            auditor = VendoringAuditor()
            vend_res = auditor.audit_directory(self.target_dir)
            t_vend = (time.perf_counter() - t0) * 1000.0

            vend_error = "; ".join(vend_res.violations) if not vend_res.passed else None
            self.reporter.record_phase(
                phase_id="vendoring_audit",
                title="Аудит офлайн-вендорингу та хешів",
                passed=vend_res.passed,
                duration_ms=t_vend,
                details={"packages_count": vend_res.total_packages_found},
                error=vend_error,
            )

            # 2. Фаза 2: Оркестрація zero-egress оточення
            t0 = time.perf_counter()
            orch_res = self.orchestrator.start_isolated_environment(force_mock=self.force_mock_containers)
            t_orch = (time.perf_counter() - t0) * 1000.0

            self.reporter.record_phase(
                phase_id="container_isolation",
                title="Оркестрація ізоляції (Zero-Egress)",
                passed=orch_res.zero_egress_enforced and orch_res.error is None,
                duration_ms=t_orch,
                details={"network": orch_res.network_name, "containers": len(orch_res.containers)},
                error=orch_res.error,
            )

            # 3. Фаза 3: Валідація міграцій бази даних за схемою UP -> DOWN -> UP
            t0 = time.perf_counter()
            migrator = MigrationVerifier()
            migr_res = migrator.verify_migrations()
            t_migr = (time.perf_counter() - t0) * 1000.0

            self.reporter.record_phase(
                phase_id="database_migrations",
                title="Ідемпотентність міграцій БД (up-down-up)",
                passed=migr_res.passed,
                duration_ms=t_migr,
                details={"active_tables": migr_res.active_tables},
                error=migr_res.error,
            )

            # 4. Фаза 4: Діагностика машинних контрактів здоров'я та SLA
            t0 = time.perf_counter()
            diag = DiagnosticClient()
            diag_res = diag.run_diagnostics()
            t_diag = (time.perf_counter() - t0) * 1000.0

            diag_error = None if diag_res.passed else f"Провалено {diag_res.total_probes - diag_res.passed_probes} перевірок SLA"
            self.reporter.record_phase(
                phase_id="diagnostic_contracts",
                title="Машинні діагностичні контракти (SLA)",
                passed=diag_res.passed,
                duration_ms=t_diag,
                details={"probes_passed": diag_res.passed_probes, "max_latency_ms": diag_res.max_latency_observed_ms},
                error=diag_error,
            )

        finally:
            # Гарантоване очищення інфраструктури
            self.orchestrator.teardown()

        artifact = self.reporter.generate_artifact(self.system_name)
        self.reporter.print_console_summary(artifact)

        return artifact.gate_passed


def main() -> None:
    parser = argparse.ArgumentParser(
        description="Clean-Room Acceptance Harness: Автоматизоване інженерне приймання коду підрядника."
    )
    parser.add_argument("--target-dir", default=".", help="Шлях до перевірюваного репозиторію проєкту.")
    parser.add_argument("--system-name", default="Delivered-Core-System", help="Офіційна назва системи для акта.")
    parser.add_argument("--output-json", default="acceptance_report.json", help="Файл для збереження JSON-звіту.")
    parser.add_argument("--output-md", default="acceptance_report.md", help="Файл для збереження Markdown-звіту.")
    parser.add_argument("--mock-docker", action="store_true", default=True, help="Використовувати безпечну емуляцію контейнерів.")
    parser.add_argument("--secret-key", default="cleanroom-sovereign-acceptance-secret", help="Ключ для HMAC-підпису.")

    args = parser.parse_args()

    harness = CleanRoomHarness(
        target_dir=args.target_dir,
        signing_key=args.secret_key,
        system_name=args.system_name,
        force_mock_containers=args.mock_docker,
    )

    passed = harness.run_all_acceptance_gates()

    # Збереження артефактів звітності
    artifact = harness.reporter.generate_artifact(args.system_name)
    harness.reporter.save_json(args.output_json, artifact)
    Path(args.output_md).write_text(harness.reporter.generate_markdown(artifact), encoding="utf-8")

    sys.exit(0 if passed else 1)


if __name__ == "__main__":
    main()
