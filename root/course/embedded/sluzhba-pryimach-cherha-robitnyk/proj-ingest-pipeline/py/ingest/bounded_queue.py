"""Демпферна черга між приймачем і робітниками.

Обмежена місткість, два ватерпости з гістерезисом (80% вгору, 50% вниз)
і витіснення найстарішого пакета, коли місця не лишилося зовсім.
"""

from __future__ import annotations

import asyncio
from collections import deque
from enum import Enum, auto

from .wire_format import RawPacket

HIGH_RATIO = 0.80
LOW_RATIO = 0.50


class PopStatus(Enum):
    OK = auto()
    TIMEOUT = auto()
    CLOSED = auto()


class PushStatus(Enum):
    STORED = auto()
    EVICTED_OLDEST = auto()
    REJECTED_CLOSED = auto()


class BoundedQueue:
    def __init__(self, capacity: int) -> None:
        self._capacity = capacity
        self._high = int(capacity * HIGH_RATIO)
        self._low = int(capacity * LOW_RATIO)
        self._items: deque[RawPacket] = deque()
        self._cv = asyncio.Condition()
        self._closed = False
        # Прапорець читає приймач на кожному пакеті — тримаємо його простим полем.
        self.backpressure = False
        self.dropped = 0

    async def push(self, packet: RawPacket) -> PushStatus:
        async with self._cv:
            if self._closed:
                return PushStatus.REJECTED_CLOSED

            status = PushStatus.STORED
            if len(self._items) >= self._capacity:
                # Свіжі дані цінніші за протухлі — викидаємо найстаріший пакет.
                self._items.popleft()
                self.dropped += 1
                status = PushStatus.EVICTED_OLDEST

            self._items.append(packet)
            if len(self._items) >= self._high:
                self.backpressure = True

            self._cv.notify()
            return status

    async def pop(self, timeout: float) -> tuple[PopStatus, RawPacket | None]:
        loop = asyncio.get_running_loop()
        deadline = loop.time() + timeout

        async with self._cv:
            while not self._items and not self._closed:
                remaining = deadline - loop.time()
                if remaining <= 0:
                    return PopStatus.TIMEOUT, None
                try:
                    # Condition.wait() перед виходом знову бере замок — навіть коли
                    # її скасував wait_for, тож повертатися звідси безпечно.
                    await asyncio.wait_for(self._cv.wait(), remaining)
                except asyncio.TimeoutError:
                    return PopStatus.TIMEOUT, None

            if not self._items:
                return PopStatus.CLOSED, None  # чергу закрили і вона допита до дна

            packet = self._items.popleft()
            if len(self._items) <= self._low:
                self.backpressure = False
            return PopStatus.OK, packet

    async def close(self) -> None:
        """Закриття не рве обробку: робітники спершу допивають залишок черги."""
        async with self._cv:
            self._closed = True
            self._cv.notify_all()

    def __len__(self) -> int:
        return len(self._items)
