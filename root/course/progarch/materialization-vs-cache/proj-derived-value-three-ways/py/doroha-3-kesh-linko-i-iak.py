# Однополітність у процесі: збіг промахів за ключем склеюється в ОДИН скан.
import asyncio, random

_inflight: dict[str, asyncio.Task[float]] = {}

async def monthly_kwh(home: str, month: str) -> float:
    key = f"kwh:{home}:{month}"

    hit = await cache.get(key)
    if hit is not None:                               # влучання — дешево, з пам'яті
        return float(hit)

    running = _inflight.get(key)
    if running is not None:                           # уже рахують — приєднайся
        return await running

    async def compute() -> float:
        try:
            kwh = await compute_from_source(home, month)  # ЄДИНИЙ важкий скан
            ttl = 300 + random.randint(0, 60)             # TTL із розкидом (jitter)
            await cache.set(key, kwh, ttl_seconds=ttl)
            return kwh
        finally:
            _inflight.pop(key, None)

    task = asyncio.ensure_future(compute())           # створи задачу…
    _inflight[key] = task                             # …і зареєструй БЕЗ await між
    return await task
