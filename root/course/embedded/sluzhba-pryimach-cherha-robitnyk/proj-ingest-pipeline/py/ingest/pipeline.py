"""Приймач, вирівнювач часової шкали, сховище пакетного запису й робітник розбору."""

from __future__ import annotations

import asyncio
import time

from .bounded_queue import BoundedQueue, PopStatus, PushStatus
from .metrics import Metrics
from .wire_format import (
    DecodeError,
    NormalizedEvent,
    RawPacket,
    Reason,
    decode_frame,
    format_device_id,
    in_physical_range,
)

MAX_DATAGRAM = 1500      # MTU Ethernet
BATCH_ROWS = 256         # рядків у батчі
BATCH_MAX_AGE = 0.2      # стеля витримки батча, с
POP_TIMEOUT = 0.02       # крок циклу робітника, с
MAX_LAG_MS = 5000        # більше — це вже не лаг, а перезавантаження пристрою


class IngestReceiver:
    """Зафіксувати t_recv, загорнути байти в конверт, віддати в чергу. Крапка.

    Жодного розбору тут немає навмисно: цикл сокета не має впиратися в CPU.
    """

    def __init__(self, queue: BoundedQueue, metrics: Metrics) -> None:
        self._queue = queue
        self._metrics = metrics

    @property
    def paused(self) -> bool:
        return self._queue.backpressure

    async def on_datagram(self, data: bytes, peer_id: int) -> bool:
        # Сміття з сокета далі приймача не йде: розмір — єдина перевірка тут.
        if not data or len(data) > MAX_DATAGRAM:
            self._metrics.on_rejected(Reason.BAD_SIZE)
            return False

        packet = RawPacket(
            data=data,
            recv_wall=time.time(),
            recv_mono=time.perf_counter(),
            peer_id=peer_id,
        )
        status = await self._queue.push(packet)
        if status is PushStatus.REJECTED_CLOSED:
            self._metrics.dropped_total += 1
            return False

        self._metrics.ingested_total += 1
        if status is PushStatus.EVICTED_OLDEST:
            # Пакет узяли, але заплатили за нього найстарішим у черзі.
            self._metrics.dropped_total += 1
        return True


class TimeAligner:
    """t_event = t_recv - lag.

    Базу «t_recv - uptime» тримаємо за мінімумом спостережень: найшвидша доставка
    найближча до істини, решта затримок — черги в мережі й у нас самих.
    """

    def __init__(self) -> None:
        self._base_ms: dict[int, int] = {}

    def align(self, device_id: int, uptime_ms: int, recv_wall: float) -> tuple[float, int]:
        observed = int(recv_wall * 1000) - uptime_ms
        base = self._base_ms.get(device_id)
        # Менша база — швидша доставка. Стрибок понад стелю означає, що пристрій
        # перезавантажився (uptime почався з нуля) — базу перезаводимо.
        if base is None or observed < base or observed - base > MAX_LAG_MS:
            base = observed
            self._base_ms[device_id] = base

        lag_ms = observed - base
        return recv_wall - lag_ms / 1000.0, lag_ms


class EventStore:
    """Сховище приймає лише батчами: рядок за рядком база не витримає темпу."""

    def __init__(self, metrics: Metrics) -> None:
        self._metrics = metrics
        self.rows = 0
        self.batches = 0

    async def write_batch(self, rows: list[NormalizedEvent]) -> None:
        if not rows:
            return
        await asyncio.sleep(0.001)  # імітація круга до бази даних
        self.rows += len(rows)
        self.batches += 1
        self._metrics.on_stored(len(rows))

        # Не логуємо кожен батч: під навантаженням лог сам стає вузьким місцем.
        if self.batches % 64 == 0:
            last = rows[-1]
            print(
                f"[сховище] батч #{self.batches}: {len(rows)} рядків, "
                f"останній {last.device_id} seq={last.seq} lag={last.lag_ms} мс"
            )


def _handle(packet: RawPacket, aligner: TimeAligner, metrics: Metrics) -> NormalizedEvent | None:
    # Затримка — від прийому до розбору: у ній сидить час, проведений у черзі.
    metrics.observe_latency(time.perf_counter() - packet.recv_mono)

    try:
        frame = decode_frame(packet.data)
    except DecodeError as error:
        metrics.on_rejected(error.reason)
        return None

    if not in_physical_range(frame):
        metrics.out_of_range_total += 1
        return None

    event_time, lag_ms = aligner.align(frame.device_id, frame.uptime_ms, packet.recv_wall)
    return NormalizedEvent(
        device_id=format_device_id(frame.device_id),
        event_time=event_time,
        lag_ms=lag_ms,
        temperature_c=round(frame.temperature_c, 2),
        humidity_pct=round(frame.humidity_pct, 2),
        battery_v=round(frame.battery_v, 3),
        seq=frame.seq,
    )


async def telemetry_worker(
    worker_id: int,
    queue: BoundedQueue,
    aligner: TimeAligner,
    store: EventStore,
    metrics: Metrics,
) -> None:
    batch: list[NormalizedEvent] = []
    last_flush = time.perf_counter()

    while True:
        status, packet = await queue.pop(POP_TIMEOUT)
        if status is PopStatus.CLOSED:
            break
        if status is PopStatus.OK and packet is not None:
            event = _handle(packet, aligner, metrics)
            if event is not None:
                batch.append(event)

        # Батч їде або коли набрався, або коли перший рядок у ньому зачекався:
        # без другої умови рідкий трафік лежав би в пам'яті годинами.
        now = time.perf_counter()
        if len(batch) >= BATCH_ROWS or (batch and now - last_flush >= BATCH_MAX_AGE):
            await store.write_batch(batch)
            batch = []
            last_flush = now

    # Коректне завершення: залишок батча йде у сховище, а не в нікуди.
    await store.write_batch(batch)
    del worker_id
