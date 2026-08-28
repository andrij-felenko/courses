import logging
import random
import threading
from typing import Any, Callable
from psycopg_pool import ConnectionPool

CLAIM = """
UPDATE jobs SET run_at = now() + make_interval(secs => %s),
                attempts = attempts + 1, locked_by = %s
 WHERE id IN (SELECT id FROM jobs
               WHERE status = 'ready' AND run_at <= now()
                 AND attempts < max_attempts
               ORDER BY run_at, id LIMIT %s FOR UPDATE SKIP LOCKED)
RETURNING id, kind, payload, attempts, max_attempts
"""

LEASE_S = 60
Handler = Callable[[str, Any], None]


def run_worker(pool: ConnectionPool, me: str, handle: Handler, stop: threading.Event) -> None:
    while not stop.is_set():
        with pool.connection() as conn:                       # транзакція на запит
            rows = conn.execute(CLAIM, (LEASE_S, me, 1)).fetchall()
        if not rows:                                          # черга порожня — почекати з розкидом
            stop.wait(0.5 + random.random() * 0.5)
            continue
        for row in rows:
            _run_one(pool, me, handle, *row)


def _run_one(pool: ConnectionPool, me: str, handle: Handler,
             job_id: int, kind: str, payload: Any, attempts: int, max_attempts: int) -> None:
    failure: str | None = None
    try:
        handle(kind, payload)          # дедлайн задачі — таймаути всередині обробника
    except Exception as exc:
        failure = str(exc)

    try:
        with pool.connection() as conn:
            if failure is None:
                conn.execute("DELETE FROM jobs WHERE id = %s AND locked_by = %s", (job_id, me))
            elif attempts >= max_attempts:
                conn.execute("UPDATE jobs SET status = 'dead', last_error = %s, run_at = now()"
                             " WHERE id = %s AND locked_by = %s", (failure, job_id, me))
            else:
                conn.execute("UPDATE jobs SET run_at = now() + make_interval(secs => %s),"
                             " last_error = %s WHERE id = %s AND locked_by = %s",
                             (backoff(attempts), failure, job_id, me))
    except Exception:
        # рядок не закрито — задачу поверне оренда, тож просто пишемо в журнал
        logging.exception("задача %s: рядок не закрито", job_id)


def backoff(attempt: int) -> float:
    """Затримка в секундах: база·2^(спроба−1), зі стелею й розкидом."""
    base, ceil = 5.0, 3600.0
    d = min(ceil, base * 2 ** (attempt - 1))
    return d / 2 + random.random() * d / 2          # розкид: [d/2 .. d]
