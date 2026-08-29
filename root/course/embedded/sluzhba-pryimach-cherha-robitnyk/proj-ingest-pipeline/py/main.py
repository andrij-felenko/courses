"""Прогін конвеєра під двома джерелами: ввічливим (чує зворотний тиск) і залповим.

Другий і показує, коли спрацьовує витіснення найстарішого пакета.
"""

from __future__ import annotations

import asyncio
import time

from ingest.bounded_queue import BoundedQueue
from ingest.metrics import Metrics
from ingest.pipeline import EventStore, IngestReceiver, TimeAligner, telemetry_worker
from ingest.wire_format import Reason, encode_frame

POLITE_FRAMES = 20000
FLOOD_FRAMES = 5000
WORKERS = 4

DEVICES = [0x000104A2, 0x000104A3, 0x000104B0, 0x00020001]


class Source:
    """Стан одного пристрою: власний uptime і власна нумерація кадрів."""

    def __init__(self, device_id: int) -> None:
        self.device_id = device_id
        self.uptime_ms = 0
        self.seq = 0


def make_frame(source: Source, index: int) -> bytes:
    """Кадр із реального пристрою — з тими самими вадами, що трапляються в полі."""
    source.uptime_ms += 100  # пристрій шле раз на 100 мс

    raw_temp = 2345 + (index % 40)   # ~23.45 °C
    raw_hum = 5820 + (index % 15)    # ~58.2 %
    raw_vbat = 3820                  # 3.82 В

    if index % 53 == 0:
        raw_temp = 20000  # 200 °C — давач відвалився, дані невалідні

    frame = bytearray(
        encode_frame(source.device_id, source.uptime_ms, raw_temp, raw_hum, raw_vbat,
                     source.seq, 0x0007)
    )
    source.seq = (source.seq + 1) & 0xFFFF

    if index % 97 == 0:
        frame[13] ^= 0x01  # біт помер у каналі — CRC не зійдеться
    if index % 211 == 0:
        frame[0] = 0x00    # збилася межа кадру — магія не та
    return bytes(frame)


async def main() -> None:
    metrics = Metrics()
    queue = BoundedQueue(capacity=1024)
    aligner = TimeAligner()
    store = EventStore(metrics)
    receiver = IngestReceiver(queue, metrics)

    workers = [
        asyncio.create_task(telemetry_worker(i, queue, aligner, store, metrics))
        for i in range(WORKERS)
    ]
    sources = [Source(device_id) for device_id in DEVICES]

    print(f"Конвеєр прийому телеметрії: {WORKERS} робітники, черга на 1024 пакети")
    started = time.perf_counter()
    throttle_waits = 0

    # Фаза 1: TCP-подібне джерело. Побачив зворотний тиск — притримало читання сокета.
    for i in range(POLITE_FRAMES):
        while receiver.paused:
            throttle_waits += 1
            await asyncio.sleep(0.0002)
        await receiver.on_datagram(make_frame(sources[i % len(sources)], i), i % 64)
        if i % 64 == 0:
            # Черга під незайнятим замком не поступається циклом — поступаємося самі,
            # інакше приймач заморить робітників голодом у тому самому потоці.
            await asyncio.sleep(0)

    # Фаза 2: UDP-залп. Притримати відправника неможливо — черга рятується сама.
    for i in range(FLOOD_FRAMES):
        await receiver.on_datagram(make_frame(sources[i % len(sources)], i), i % 64)
        if i % 64 == 0:
            await asyncio.sleep(0)

    await queue.close()          # приймач замовк
    await asyncio.gather(*workers)  # робітники допивають чергу і скидають батчі

    elapsed = max(time.perf_counter() - started, 1e-6)
    total = POLITE_FRAMES + FLOOD_FRAMES
    print("\n--- Підсумок прийому ---")
    print(f"Надіслано кадрів:      {total}")
    print(f"Прийнято в чергу:      {metrics.ingested_total}")
    print(f"Витіснено з черги:     {metrics.dropped_total}")
    print(f"Пауз зворотного тиску: {throttle_waits}")
    print(f"Биті CRC:              {metrics.rejected[Reason.CRC_MISMATCH.value]}")
    print(f"Збита межа кадру:      {metrics.rejected[Reason.BAD_MAGIC.value]}")
    print(f"Поза діапазоном:       {metrics.out_of_range_total}")
    print(f"Записано рядків:       {store.rows} у {store.batches} батчах")
    print(f"Час прогону:           {elapsed:.3f} с")
    print(f"Темп:                  {total / elapsed:.0f} кадрів/с\n")
    print(metrics.render_prometheus())


if __name__ == "__main__":
    asyncio.run(main())
