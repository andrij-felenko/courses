"""
Репозиторій Outbox: PostgreSQL + asyncpg (з підтримкою in-memory fallback для тестів).
"""

import asyncio
import copy
import time
import uuid
from typing import Any, Optional

from models import OutboxEvent, OutboxStatus

# Еталонні SQL-запити для PostgreSQL + asyncpg
POSTGRES_SCHEMA_SQL = """
CREATE TABLE IF NOT EXISTS outbox_events (
    id UUID PRIMARY KEY,
    aggregate_type VARCHAR(64) NOT NULL,
    aggregate_id VARCHAR(64) NOT NULL,
    event_type VARCHAR(64) NOT NULL,
    payload JSONB NOT NULL,
    idempotency_key VARCHAR(128) NOT NULL UNIQUE,
    status VARCHAR(32) NOT NULL DEFAULT 'PENDING',
    attempts INT NOT NULL DEFAULT 0,
    max_attempts INT NOT NULL DEFAULT 3,
    next_retry_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    locked_at TIMESTAMPTZ,
    locked_by VARCHAR(64),
    last_error TEXT,
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    updated_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

-- Частковий індекс для надшвидкої вибірки лише активних записів без сканування архіву
CREATE INDEX IF NOT EXISTS idx_outbox_active_fetch
ON outbox_events (next_retry_at)
WHERE status IN ('PENDING', 'PROCESSING');
"""

POSTGRES_FETCH_SKIP_LOCKED_SQL = """
WITH eligible AS (
    SELECT id
    FROM outbox_events
    WHERE (status = 'PENDING' AND next_retry_at <= NOW())
       OR (status = 'PROCESSING' AND locked_at < NOW() - $2::interval)
    ORDER BY next_retry_at ASC
    FOR UPDATE SKIP LOCKED
    LIMIT $1
)
UPDATE outbox_events e
SET status = 'PROCESSING',
    locked_at = NOW(),
    locked_by = $3,
    updated_at = NOW()
FROM eligible
WHERE e.id = eligible.id
RETURNING e.id, e.aggregate_type, e.aggregate_id, e.event_type, e.payload,
          e.idempotency_key, e.status, e.attempts, e.max_attempts,
          EXTRACT(EPOCH FROM e.next_retry_at) AS next_retry_at,
          EXTRACT(EPOCH FROM e.locked_at) AS locked_at,
          e.locked_by, e.last_error,
          EXTRACT(EPOCH FROM e.created_at) AS created_at,
          EXTRACT(EPOCH FROM e.updated_at) AS updated_at;
"""


class OutboxRepository:
    """
    Репозиторій Outbox з підтримкою конкурентної вибірки SKIP LOCKED.
    Включає повноцінну транзакційну підтримку як для підключення до PostgreSQL
    через asyncpg, так і високонадійний імітатор реляційної пам'яті з блокуванням рядків
    для автономних середовищ та тестових стендів.
    """

    def __init__(self, pg_pool: Optional[Any] = None):
        self.pg_pool = pg_pool
        self._events: dict[str, OutboxEvent] = {}
        self._lock = asyncio.Lock()

    async def init_schema(self) -> None:
        """Ініціалізує схему таблиці та часткових індексів у PostgreSQL."""
        if self.pg_pool:
            async with self.pg_pool.acquire() as conn:
                await conn.execute(POSTGRES_SCHEMA_SQL)

    async def save_within_transaction(
        self,
        aggregate_type: str,
        aggregate_id: str,
        event_type: str,
        payload: dict[str, Any],
        idempotency_key: Optional[str] = None,
        max_attempts: int = 3,
        conn: Optional[Any] = None,
    ) -> OutboxEvent:
        """
        Атомарно зберігає подію аутбоксу в межах єдиної транзакції бази даних
        разом із мутацією бізнес-сутності, усуваючи пастку Dual-Write Hazard.
        """
        event_id = str(uuid.uuid4())
        now = time.time()
        idem_key = idempotency_key or f"idem-{event_id}"

        event = OutboxEvent(
            id=event_id,
            aggregate_type=aggregate_type,
            aggregate_id=aggregate_id,
            event_type=event_type,
            payload=payload,
            idempotency_key=idem_key,
            status=OutboxStatus.PENDING,
            attempts=0,
            max_attempts=max_attempts,
            next_retry_at=now,
            created_at=now,
            updated_at=now,
        )

        if self.pg_pool and conn:
            import json
            sql = """
            INSERT INTO outbox_events (
                id, aggregate_type, aggregate_id, event_type, payload,
                idempotency_key, status, attempts, max_attempts, next_retry_at,
                created_at, updated_at
            ) VALUES ($1, $2, $3, $4, $5, $6, $7, $8, $9, to_timestamp($10), to_timestamp($11), to_timestamp($12));
            """
            await conn.execute(
                sql,
                uuid.UUID(event.id), event.aggregate_type, event.aggregate_id,
                event.event_type, json.dumps(event.payload), event.idempotency_key,
                event.status.value, event.attempts, event.max_attempts,
                event.next_retry_at, event.created_at, event.updated_at,
            )
        else:
            async with self._lock:
                self._events[event.id] = event

        return event

    async def fetch_batch_skip_locked(
        self,
        batch_size: int,
        worker_id: str,
        lease_timeout_s: float = 3.0,
    ) -> list[OutboxEvent]:
        """
        Конкурентна вибірка готових задач за семантикою SELECT ... FOR UPDATE SKIP LOCKED.
        Пропускає рядки, що вже обробляються паралельними воркерами, запобігаючи дедлокам
        і очікуванню транзакцій. Автоматично перехоплює завислі блокування за лізингом.
        """
        if self.pg_pool:
            async with self.pg_pool.acquire() as conn:
                interval_str = f"{lease_timeout_s} seconds"
                records = await conn.fetch(POSTGRES_FETCH_SKIP_LOCKED_SQL, batch_size, interval_str, worker_id)
                import json
                result = []
                for r in records:
                    p = r["payload"] if isinstance(r["payload"], dict) else json.loads(r["payload"])
                    result.append(OutboxEvent(
                        id=str(r["id"]),
                        aggregate_type=r["aggregate_type"],
                        aggregate_id=r["aggregate_id"],
                        event_type=r["event_type"],
                        payload=p,
                        idempotency_key=r["idempotency_key"],
                        status=OutboxStatus(r["status"]),
                        attempts=r["attempts"],
                        max_attempts=r["max_attempts"],
                        next_retry_at=r["next_retry_at"],
                        locked_at=r["locked_at"],
                        locked_by=r["locked_by"],
                        last_error=r["last_error"],
                        created_at=r["created_at"],
                        updated_at=r["updated_at"],
                    ))
                return result

        now = time.time()
        selected: list[OutboxEvent] = []

        async with self._lock:
            candidates = sorted(self._events.values(), key=lambda e: e.next_retry_at)

            for event in candidates:
                if len(selected) >= batch_size:
                    break

                is_pending = (event.status == OutboxStatus.PENDING and event.next_retry_at <= now)
                is_stale_lock = (
                    event.status == OutboxStatus.PROCESSING
                    and event.locked_at is not None
                    and (now - event.locked_at) >= lease_timeout_s
                )

                if is_pending or is_stale_lock:
                    event.status = OutboxStatus.PROCESSING
                    event.locked_at = now
                    event.locked_by = worker_id
                    event.updated_at = now
                    selected.append(copy.deepcopy(event))

        return selected

    async def mark_processed(self, event_id: str) -> None:
        """Переводить подію в статус успішно доставленої (PROCESSED) і знімає лок."""
        now = time.time()
        if self.pg_pool:
            sql = """
            UPDATE outbox_events
            SET status = 'PROCESSED', locked_at = NULL, locked_by = NULL, updated_at = to_timestamp($2)
            WHERE id = $1;
            """
            async with self.pg_pool.acquire() as conn:
                await conn.execute(sql, uuid.UUID(event_id), now)
        else:
            async with self._lock:
                if event_id in self._events:
                    e = self._events[event_id]
                    e.status = OutboxStatus.PROCESSED
                    e.locked_at = None
                    e.locked_by = None
                    e.updated_at = now

    async def schedule_retry(
        self,
        event_id: str,
        attempts: int,
        next_retry_at: float,
        error_msg: str,
    ) -> None:
        """Планує повторну спробу з оновленням лічильника та часу наступного запуску."""
        now = time.time()
        if self.pg_pool:
            sql = """
            UPDATE outbox_events
            SET status = 'PENDING', attempts = $2, next_retry_at = to_timestamp($3),
                last_error = $4, locked_at = NULL, locked_by = NULL, updated_at = to_timestamp($5)
            WHERE id = $1;
            """
            async with self.pg_pool.acquire() as conn:
                await conn.execute(sql, uuid.UUID(event_id), attempts, next_retry_at, error_msg, now)
        else:
            async with self._lock:
                if event_id in self._events:
                    e = self._events[event_id]
                    e.status = OutboxStatus.PENDING
                    e.attempts = attempts
                    e.next_retry_at = next_retry_at
                    e.last_error = error_msg
                    e.locked_at = None
                    e.locked_by = None
                    e.updated_at = now

    async def move_to_dead_letter(
        self,
        event_id: str,
        attempts: int,
        error_msg: str,
    ) -> None:
        """Ізолює отруйне повідомлення в карантині (DEAD_LETTER) для ручного розбору."""
        now = time.time()
        if self.pg_pool:
            sql = """
            UPDATE outbox_events
            SET status = 'DEAD_LETTER', attempts = $2, last_error = $3,
                locked_at = NULL, locked_by = NULL, updated_at = to_timestamp($4)
            WHERE id = $1;
            """
            async with self.pg_pool.acquire() as conn:
                await conn.execute(sql, uuid.UUID(event_id), attempts, error_msg, now)
        else:
            async with self._lock:
                if event_id in self._events:
                    e = self._events[event_id]
                    e.status = OutboxStatus.DEAD_LETTER
                    e.attempts = attempts
                    e.last_error = error_msg
                    e.locked_at = None
                    e.locked_by = None
                    e.updated_at = now

    async def get_stats(self) -> dict[str, int]:
        """Повертає статистику розподілу станів подій."""
        stats = {
            OutboxStatus.PENDING.value: 0,
            OutboxStatus.PROCESSING.value: 0,
            OutboxStatus.PROCESSED.value: 0,
            OutboxStatus.DEAD_LETTER.value: 0,
        }
        if self.pg_pool:
            sql = "SELECT status, count(*) AS cnt FROM outbox_events GROUP BY status;"
            async with self.pg_pool.acquire() as conn:
                rows = await conn.fetch(sql)
                for r in rows:
                    stats[r["status"]] = r["cnt"]
        else:
            async with self._lock:
                for e in self._events.values():
                    stats[e.status.value] += 1
        return stats
