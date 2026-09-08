"""
migration_verifier.py — Верифікація двосторонньої ідемпотентності схеми бази даних.
Виконує повний цикл up -> down -> up та порівнює криптографічні відбитки структури БД.
"""

from dataclasses import dataclass, field
from pathlib import Path
import hashlib
import sqlite3
from typing import Optional


@dataclass
class MigrationStep:
    """Пара SQL-сценаріїв прямої та зворотної міграції."""

    version: str
    name: str
    up_sql: str
    down_sql: str


@dataclass
class VerificationResult:
    """Результат перевірки двосторонньої ідемпотентності міграцій."""

    is_idempotent: bool
    applied_count: int
    rolled_back_count: int
    initial_up_hash: str
    reapplied_up_hash: str
    empty_slate_verified: bool
    errors: list[str] = field(default_factory=list)


class MigrationVerifier:
    """
    Валідатор схеми даних.

    Гарантує, що система підтримує повністю відтворюваний життєвий цикл бази даних:
    1. Up-фаза: послідовне накатування всіх міграцій від початкового стану.
    2. Down-фаза: повний відкат у зворотному порядку до абсолютно чистого аркуша.
    3. Re-Up-фаза: повторне накатування та порівняння структури схеми.
    """

    def load_migrations_from_dir(self, migrations_dir: Path) -> list[MigrationStep]:
        """
        Завантажує та парсить пари міграцій з файлів виду:
        '001_initial.up.sql' та '001_initial.down.sql'.
        """
        if not migrations_dir.is_dir():
            return []

        up_files = sorted(migrations_dir.glob("*.up.sql"))
        steps: list[MigrationStep] = []

        for up_file in up_files:
            prefix = up_file.name[:-7]  # Відрізаємо '.up.sql'
            down_file = migrations_dir / f"{prefix}.down.sql"

            up_sql = up_file.read_text(encoding="utf-8")
            down_sql = down_file.read_text(encoding="utf-8") if down_file.is_file() else ""

            parts = prefix.split("_", 1)
            version = parts[0]
            name = parts[1] if len(parts) > 1 else prefix

            steps.append(
                MigrationStep(
                    version=version,
                    name=name,
                    up_sql=up_sql,
                    down_sql=down_sql,
                )
            )

        return steps

    def _get_schema_fingerprint(self, conn: sqlite3.Connection) -> str:
        """
        Обчислює детермінований SHA-256 хеш поточної схеми таблиць, колонок та індексів.
        """
        cursor = conn.cursor()
        cursor.execute(
            """
            SELECT type, name, sql
            FROM sqlite_master
            WHERE name NOT LIKE 'sqlite_%'
            ORDER BY type ASC, name ASC;
            """
        )
        rows = cursor.fetchall()
        schema_dump = "\n".join(f"{r[0]}:{r[1]}:{r[2] or ''}" for r in rows)
        return hashlib.sha256(schema_dump.encode("utf-8")).hexdigest()

    def _get_active_tables(self, conn: sqlite3.Connection) -> list[str]:
        """Повертає список існуючих користувацьких таблиць у БД."""
        cursor = conn.cursor()
        cursor.execute(
            """
            SELECT name FROM sqlite_master
            WHERE type='table' AND name NOT LIKE 'sqlite_%';
            """
        )
        return [row[0] for row in cursor.fetchall()]

    def verify_migrations(
        self, steps: list[MigrationStep], db_path: str = ":memory:"
    ) -> VerificationResult:
        """
        Запускає повний цикл валідації: up -> down -> up.
        """
        errors: list[str] = []
        if not steps:
            return VerificationResult(
                is_idempotent=False,
                applied_count=0,
                rolled_back_count=0,
                initial_up_hash="",
                reapplied_up_hash="",
                empty_slate_verified=False,
                errors=["Міграції не знайдено для перевірки."],
            )

        # Перевірка наявності down-скриптів для кожної міграції
        for step in steps:
            if not step.down_sql.strip():
                errors.append(
                    f"Міграція {step.version}_{step.name} не має відповідного down-скрипту для відкату!"
                )

        conn = sqlite3.connect(db_path)
        try:
            # ФАЗА 1: Початкове накочування (UP)
            applied_up_count = 0
            for step in steps:
                conn.executescript(step.up_sql)
                applied_up_count += 1
            initial_up_hash = self._get_schema_fingerprint(conn)

            # ФАЗА 2: Повний відкат у зворотному порядку (DOWN)
            rolled_back_count = 0
            for step in reversed(steps):
                if step.down_sql.strip():
                    conn.executescript(step.down_sql)
                    rolled_back_count += 1

            # Перевірка, що після відкату не залишилося артефактних таблиць
            remaining_tables = self._get_active_tables(conn)
            empty_slate_verified = (len(remaining_tables) == 0)
            if not empty_slate_verified:
                errors.append(
                    f"Після відкату (DOWN) у БД залишилися таблиці: {remaining_tables}. Відкат не є чистим!"
                )

            # ФАЗА 3: Повторне накочування (RE-UP)
            for step in steps:
                conn.executescript(step.up_sql)

            reapplied_up_hash = self._get_schema_fingerprint(conn)

            # Перевірка ідентичності схеми
            if initial_up_hash != reapplied_up_hash:
                errors.append(
                    "Невідповідність схеми: хеш повторно розгорнутої БД відрізняється від початкового."
                )

            is_idempotent = (len(errors) == 0) and empty_slate_verified

            return VerificationResult(
                is_idempotent=is_idempotent,
                applied_count=applied_up_count,
                rolled_back_count=rolled_back_count,
                initial_up_hash=initial_up_hash,
                reapplied_up_hash=reapplied_up_hash,
                empty_slate_verified=empty_slate_verified,
                errors=errors,
            )

        except sqlite3.Error as ex:
            errors.append(f"Помилка виконання SQL під час міграцій: {ex}")
            return VerificationResult(
                is_idempotent=False,
                applied_count=0,
                rolled_back_count=0,
                initial_up_hash="",
                reapplied_up_hash="",
                empty_slate_verified=False,
                errors=errors,
            )
        finally:
            conn.close()
