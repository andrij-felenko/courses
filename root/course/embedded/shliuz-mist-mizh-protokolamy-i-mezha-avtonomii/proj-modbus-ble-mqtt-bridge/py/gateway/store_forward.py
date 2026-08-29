"""Буфер Store-and-Forward: дві черги в одному об'єкті.

Свіжа черга коротка й має пріоритет; переповнившись, вона віддає найстаріше в
архівну, а переповнена архівна витісняє найдавніше й рахує втрати. Тому щойно
зняті показники ніколи не чекають за спиною в тисяч старих записів.

Повідомлення знімається не тоді, коли пішло в сокет, а тоді, коли брокер його
підтвердив: ``peek`` видає копію в оренду, ``commit`` забирає оригінал.
"""

from __future__ import annotations

import asyncio
from collections import deque
from dataclasses import dataclass


@dataclass(frozen=True, slots=True)
class TelemetryMessage:
    topic: str
    payload: str
    seq: int


@dataclass(frozen=True, slots=True)
class Lease:
    message: TelemetryMessage
    from_backlog: bool


@dataclass(frozen=True, slots=True)
class Stats:
    fresh: int
    backlog: int
    dropped: int


class StoreForward:
    def __init__(self, fresh_capacity: int = 64, backlog_capacity: int = 4096) -> None:
        self._fresh: deque[TelemetryMessage] = deque()
        self._backlog: deque[TelemetryMessage] = deque()
        self._fresh_capacity = fresh_capacity
        self._backlog_capacity = backlog_capacity
        self._dropped = 0
        self._ready = asyncio.Condition()

    async def publish(self, message: TelemetryMessage) -> None:
        async with self._ready:
            if len(self._fresh) >= self._fresh_capacity:
                # Канал стоїть: найстаріше зі свіжого стає історією.
                aged = self._fresh.popleft()
                if len(self._backlog) >= self._backlog_capacity:
                    self._backlog.popleft()
                    self._dropped += 1  # розрив у seq покаже серверу масштаб втрати
                self._backlog.append(aged)
            self._fresh.append(message)
            self._ready.notify()

    async def peek(self, timeout: float) -> Lease | None:
        async with self._ready:
            if not self._fresh and not self._backlog:
                try:
                    await asyncio.wait_for(
                        self._ready.wait_for(lambda: bool(self._fresh or self._backlog)),
                        timeout,
                    )
                except asyncio.TimeoutError:
                    return None
            if self._fresh:
                return Lease(self._fresh[0], from_backlog=False)
            return Lease(self._backlog[0], from_backlog=True)

    async def commit(self, lease: Lease) -> None:
        async with self._ready:
            queue = self._backlog if lease.from_backlog else self._fresh
            # Поки ми чекали PUBACK, витіснення могло зсунути голову черги:
            # знімаємо лише те саме повідомлення, яке справді пішло в сокет.
            if queue and queue[0].seq == lease.message.seq:
                queue.popleft()

    def stats(self) -> Stats:
        return Stats(len(self._fresh), len(self._backlog), self._dropped)
