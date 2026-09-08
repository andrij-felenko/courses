"""
Фоновий асинхронний воркер для опитування таблиці Outbox і диспетчеризації подій.
"""

import asyncio
import time
from typing import Optional

from http_client import IdempotentClient
from models import NonRetryableError, OutboxEvent, RetryableError, WorkerConfig
from repository import OutboxRepository
from retry import compute_full_jitter


class OutboxWorker:
    """
    Фоновий асинхронний диспетчер подій Transactional Outbox.
    Здійснює пакетне опитування репозиторію через SKIP LOCKED, обмежує одночасність
    мережевих викликів за допомогою семафора та керує станами доставки.
    """

    def __init__(
        self,
        worker_id: str,
        repo: OutboxRepository,
        client: IdempotentClient,
        target_url: str,
        config: Optional[WorkerConfig] = None,
    ):
        self.worker_id = worker_id
        self.repo = repo
        self.client = client
        self.target_url = target_url
        self.config = config or WorkerConfig()
        self._semaphore = asyncio.Semaphore(self.config.max_concurrent_tasks)
        self._active_tasks: set[asyncio.Task] = set()

    async def run(self, stop_event: asyncio.Event) -> None:
        """Головний фоновий цикл воркера."""
        while not stop_event.is_set():
            try:
                batch = await self.repo.fetch_batch_skip_locked(
                    batch_size=self.config.batch_size,
                    worker_id=self.worker_id,
                    lease_timeout_s=self.config.lease_timeout_s,
                )

                if not batch:
                    try:
                        await asyncio.wait_for(stop_event.wait(), timeout=self.config.poll_interval_s)
                    except asyncio.TimeoutError:
                        pass
                    continue

                for event in batch:
                    task = asyncio.create_task(self._process_event_safe(event))
                    self._active_tasks.add(task)
                    task.add_done_callback(self._active_tasks.discard)

            except Exception as loop_err:
                print(f"[{self.worker_id}] Помилка у циклі опитування: {loop_err}")
                await asyncio.sleep(self.config.poll_interval_s)

        if self._active_tasks:
            await asyncio.gather(*self._active_tasks, return_exceptions=True)

    async def _process_event_safe(self, event: OutboxEvent) -> None:
        async with self._semaphore:
            await self._process_event(event)

    async def _process_event(self, event: OutboxEvent) -> None:
        try:
            resp = await self.client.send_event(self.target_url, event)
            if resp.is_success:
                await self.repo.mark_processed(event.id)

        except NonRetryableError as fatal_err:
            attempts = event.attempts + 1
            await self.repo.move_to_dead_letter(event.id, attempts, str(fatal_err))

        except RetryableError as transient_err:
            attempts = event.attempts + 1
            if attempts >= event.max_attempts:
                await self.repo.move_to_dead_letter(
                    event.id, attempts,
                    f"Вичерпано ліміт спроб ({attempts}/{event.max_attempts}): {transient_err}"
                )
            else:
                jitter_delay = compute_full_jitter(
                    attempt=attempts,
                    base_delay=self.config.base_delay_s,
                    max_delay=self.config.max_delay_s,
                )
                next_retry = time.time() + jitter_delay
                await self.repo.schedule_retry(
                    event.id, attempts, next_retry, str(transient_err)
                )

        except Exception as unexpected_err:
            attempts = event.attempts + 1
            await self.repo.schedule_retry(
                event.id, attempts, time.time() + self.config.base_delay_s, f"Unexpected: {unexpected_err}"
            )
