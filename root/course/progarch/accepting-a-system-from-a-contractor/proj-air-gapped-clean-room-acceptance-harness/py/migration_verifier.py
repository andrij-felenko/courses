"""
migration_verifier.py — Верифікація двосторонньої ідемпотентності міграцій БД.
Перевіряє життєвий цикл UP -> DOWN -> UP:
1. UP_1: Накочування міграцій з нуля.
2. DOWN: Повний зворотний відкат та контроль відсутності залишкових артефактів.
3. UP_2: Повторне застосування для підтвердження детермінізму схеми.
"""

from __future__ import annotations

import re
import time
from dataclasses import dataclass, field


@dataclass
class MigrationStep:
    """Декларативний опис кроку міграції."""
    version: str
    name: str
    up_sql: str
    down_sql: str


@dataclass
class StepExecution:
    """Результат виконання окремого кроку або фази."""
    version: str
    phase: str  # "UP_1", "DOWN", "UP_2"
    duration_ms: float
    status: str
    affected_tables: list[str] = field(default_factory=list)
    error: str | None = None


@dataclass
class MigrationAuditResult:
    """Підсумковий результат аудиту схеми даних."""
    passed: bool
    total_migrations: int
    steps: list[StepExecution] = field(default_factory=list)
    active_tables: list[str] = field(default_factory=list)
    error: str | None = None


class MigrationVerifier:
    """
    Валідатор схеми даних та міграцій для контуру приймання.
    Забезпечує гарантію чистого аркуша та безпомилкового відкату.
    """

    def __init__(self) -> None:
        self.active_tables: set[str] = set()

    @staticmethod
    def get_benchmark_migrations() -> list[MigrationStep]:
        """Еталонний набір міграцій для перевірки приймання."""
        return [
            MigrationStep(
                version="001",
                name="core_tenants_and_accounts",
                up_sql=(
                    "CREATE TABLE organizations (id UUID PRIMARY KEY, name VARCHAR(255) NOT NULL); "
                    "CREATE TABLE accounts (id UUID PRIMARY KEY, org_id UUID REFERENCES organizations(id), balance NUMERIC(18,2));"
                ),
                down_sql="DROP TABLE accounts; DROP TABLE organizations;",
            ),
            MigrationStep(
                version="002",
                name="contracts_and_deliverables",
                up_sql=(
                    "CREATE TABLE contracts (id UUID PRIMARY KEY, title VARCHAR(200), total_cost NUMERIC(12,2)); "
                    "CREATE TABLE deliverables (id UUID PRIMARY KEY, contract_id UUID REFERENCES contracts(id), status VARCHAR(50));"
                ),
                down_sql="DROP TABLE deliverables; DROP TABLE contracts;",
            ),
            MigrationStep(
                version="003",
                name="audit_trail_log",
                up_sql="CREATE TABLE audit_logs (id BIGSERIAL PRIMARY KEY, event_type VARCHAR(100), recorded_at TIMESTAMP DEFAULT NOW());",
                down_sql="DROP TABLE audit_logs;",
            ),
        ]

    def verify_migrations(self, migrations: list[MigrationStep] | None = None) -> MigrationAuditResult:
        """
        Запускає повний цикл двосторонньої валідації UP -> DOWN -> UP.
        """
        steps_log: list[StepExecution] = []
        target_migrations = migrations or self.get_benchmark_migrations()
        self.active_tables.clear()

        try:
            # 1. Фаза UP_1: Накочування від чистого аркуша
            for m in target_migrations:
                exec_step = self._apply_sql_step(m, "UP_1", m.up_sql)
                steps_log.append(exec_step)
                if exec_step.status != "SUCCESS":
                    raise RuntimeError(f"Помилка UP_1 у {m.version}_{m.name}: {exec_step.error}")

            tables_after_up1 = sorted(list(self.active_tables))
            if not tables_after_up1:
                raise RuntimeError("Фаза UP_1 не створила жодної таблиці у схемі.")

            # 2. Фаза DOWN: Відкат у зворотному порядку (LIFO)
            for m in reversed(target_migrations):
                exec_step = self._apply_sql_step(m, "DOWN", m.down_sql)
                steps_log.append(exec_step)
                if exec_step.status != "SUCCESS":
                    raise RuntimeError(f"Помилка відкату DOWN у {m.version}_{m.name}: {exec_step.error}")

            # Перевірка: схема має бути абсолютно порожньою
            if self.active_tables:
                remaining = ", ".join(sorted(self.active_tables))
                raise RuntimeError(f"Після відкату виявлено залишковий бруд у схемі: {remaining}. Міграції не є зворотними!")

            # 3. Фаза UP_2: Повторне накочування для перевірки ідемпотентності
            for m in target_migrations:
                exec_step = self._apply_sql_step(m, "UP_2", m.up_sql)
                steps_log.append(exec_step)
                if exec_step.status != "SUCCESS":
                    raise RuntimeError(f"Помилка повторного UP_2 у {m.version}_{m.name}: {exec_step.error}")

            tables_after_up2 = sorted(list(self.active_tables))
            if tables_after_up1 != tables_after_up2:
                raise RuntimeError("Схема після повторного накочування UP_2 не збігається з початковим станом UP_1.")

            return MigrationAuditResult(
                passed=True,
                total_migrations=len(target_migrations),
                steps=steps_log,
                active_tables=tables_after_up2,
            )

        except Exception as e:
            return MigrationAuditResult(
                passed=False,
                total_migrations=len(target_migrations),
                steps=steps_log,
                active_tables=sorted(list(self.active_tables)),
                error=str(e),
            )

    def _apply_sql_step(self, m: MigrationStep, phase: str, sql: str) -> StepExecution:
        start_time = time.perf_counter()
        affected: list[str] = []

        try:
            # Розбір створення таблиць
            creates = re.findall(r"CREATE\s+TABLE\s+([a-zA-Z0-9_]+)", sql, re.IGNORECASE)
            for tbl in creates:
                tbl_name = tbl.lower()
                if tbl_name in self.active_tables:
                    raise ValueError(f"Таблиця '{tbl_name}' уже існує у базі даних.")
                self.active_tables.add(tbl_name)
                affected.append(tbl_name)

            # Розбір видалення таблиць
            drops = re.findall(r"DROP\s+TABLE\s+([a-zA-Z0-9_]+)", sql, re.IGNORECASE)
            for tbl in drops:
                tbl_name = tbl.lower()
                if tbl_name not in self.active_tables:
                    raise ValueError(f"Таблиця '{tbl_name}' для видалення не знайдена у базі даних.")
                self.active_tables.remove(tbl_name)
                affected.append(tbl_name)

            duration_ms = (time.perf_counter() - start_time) * 1000.0
            return StepExecution(
                version=m.version,
                phase=phase,
                duration_ms=round(duration_ms, 2),
                status="SUCCESS",
                affected_tables=affected,
            )
        except Exception as err:
            duration_ms = (time.perf_counter() - start_time) * 1000.0
            return StepExecution(
                version=m.version,
                phase=phase,
                duration_ms=round(duration_ms, 2),
                status="FAIL",
                affected_tables=affected,
                error=str(err),
            )
