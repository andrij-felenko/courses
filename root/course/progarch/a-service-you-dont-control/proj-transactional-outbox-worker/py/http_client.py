"""
Стійкий асинхронний HTTP-клієнт із підтримкою ідемпотентності та класифікацією збоїв.
"""

import asyncio
import time
from typing import Any, Optional

import aiohttp

from models import HttpResponse, NonRetryableError, OutboxEvent, RetryableError


class IdempotentClient:
    """
    Стійкий асинхронний HTTP-клієнт для виклику зовнішніх API.
    Гарантує передачу унікального заголовка Idempotency-Key для захисту
    від дублювання операцій при повторних спробах доставки.
    """

    def __init__(self, timeout_s: float = 1.5, session: Optional[aiohttp.ClientSession] = None):
        self._timeout = aiohttp.ClientTimeout(total=timeout_s, connect=0.5)
        self._external_session = session is not None
        self._session = session

    async def _get_session(self) -> aiohttp.ClientSession:
        if self._session is None or self._session.closed:
            self._session = aiohttp.ClientSession(timeout=self._timeout)
        return self._session

    async def send_event(self, url: str, event: OutboxEvent) -> HttpResponse:
        """
        Відправляє подію Outbox до партнерського сервісу.
        Класифікує результати на успіх, тимчасовий збій (Retryable) і фатальний (NonRetryable).
        """
        session = await self._get_session()
        headers = {
            "Content-Type": "application/json",
            "Idempotency-Key": event.idempotency_key,
            "X-Event-ID": event.id,
            "X-Attempt": str(event.attempts + 1),
        }
        payload = {
            "event_id": event.id,
            "aggregate_type": event.aggregate_type,
            "aggregate_id": event.aggregate_id,
            "event_type": event.event_type,
            "payload": event.payload,
        }

        start_time = time.monotonic()
        try:
            async with session.post(url, json=payload, headers=headers) as resp:
                duration_ms = (time.monotonic() - start_time) * 1000.0
                status = resp.status

                try:
                    data = await resp.json()
                except Exception:
                    data = {"raw": await resp.text()}

                # 1. Успіх (2xx): операцію виконано або підтверджено ідемпотентний кеш
                if 200 <= status < 300:
                    return HttpResponse(
                        status_code=status,
                        body=data,
                        is_success=True,
                        duration_ms=duration_ms,
                    )

                # 2. Фатальні клієнтські помилки (4xx, крім 429 Too Many Requests)
                if 400 <= status < 500 and status != 429:
                    raise NonRetryableError(
                        f"Клієнтська помилка {status} від API: {data}",
                        status_code=status,
                    )

                # 3. Серверні відмови (5xx) або обмеження швидкості (429)
                raise RetryableError(
                    f"Тимчасова відмова партнера {status}: {data}",
                    status_code=status,
                )

        except (aiohttp.ClientError, asyncio.TimeoutError, ConnectionResetError) as net_err:
            raise RetryableError(f"Мережевий збій: {type(net_err).__name__}: {net_err}") from net_err

    async def close(self) -> None:
        """Закриває сесію aiohttp при завершенні життєвого циклу."""
        if not self._external_session and self._session and not self._session.closed:
            await self._session.close()
