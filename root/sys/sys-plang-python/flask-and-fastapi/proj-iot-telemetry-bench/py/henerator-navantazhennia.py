import asyncio
import os
import time
import httpx
import numpy as np

URL = "http://127.0.0.1:8000/api/v1/telemetry"
CONCURRENCY = 1000
TOTAL_REQUESTS = 10000

PAYLOAD = {
    "device_id": "sensor_station_042",
    "temperature": 23.85,
    "humidity": 55.4,
    "battery_mv": 3280
}

HEADERS = {
    "X-Sensor-Token": "secret-station-token",
    "Content-Type": "application/json"
}

def get_context_switches(pid: int) -> tuple[int, int]:
    voluntary, nonvoluntary = 0, 0
    try:
        with open(f"/proc/{pid}/status", "r", encoding="utf-8") as f:
            for line in f:
                if line.startswith("voluntary_ctxt_switches:"):
                    voluntary = int(line.split(":")[1].strip())
                elif line.startswith("nonvoluntary_ctxt_switches:"):
                    nonvoluntary = int(line.split(":")[1].strip())
    except FileNotFoundError:
        pass
    return voluntary, nonvoluntary

async def worker(client: httpx.AsyncClient, queue: asyncio.Queue, latencies: list[float], errors: list[int]):
    while not queue.empty():
        try:
            queue.get_nowait()
        except asyncio.QueueEmpty:
            break

        start_time = time.perf_counter()
        try:
            resp = await client.post(URL, json=PAYLOAD, headers=HEADERS, timeout=10.0)
            elapsed_ms = (time.perf_counter() - start_time) * 1000.0
            if resp.status_code == 200:
                latencies.append(elapsed_ms)
            else:
                errors.append(resp.status_code)
        except Exception:
            errors.append(500)
        finally:
            queue.task_done()

async def run_benchmark():
    queue = asyncio.Queue()
    for _ in range(TOTAL_REQUESTS):
        queue.put_nowait(1)

    latencies: list[float] = []
    errors: list[int] = []

    limits = httpx.Limits(max_connections=CONCURRENCY, max_keepalive_connections=CONCURRENCY)
    async with httpx.AsyncClient(limits=limits) as client:
        start_time = time.perf_counter()
        tasks = [
            asyncio.create_task(worker(client, queue, latencies, errors))
            for _ in range(CONCURRENCY)
        ]
        await asyncio.gather(*tasks)
        total_time = time.perf_counter() - start_time

    rps = len(latencies) / total_time
    arr = np.array(latencies)
    print(f"=== Результати ({TOTAL_REQUESTS} запитів, {CONCURRENCY} клієнтів) ===")
    print(f"Загальний час:       {total_time:.2f} с")
    print(f"Пропускна здатність: {rps:.1f} req/s")
    print(f"Кількість помилок:   {len(errors)} ({len(errors)/TOTAL_REQUESTS*100:.1f}%)")
    print(f"Latency P50:         {np.percentile(arr, 50):.2f} мс")
    print(f"Latency P95:         {np.percentile(arr, 95):.2f} мс")
    print(f"Latency P99:         {np.percentile(arr, 99):.2f} мс")
    print(f"Latency Max:         {np.max(arr):.2f} мс")

if __name__ == "__main__":
    asyncio.run(run_benchmark())
