# Вимірювальний джгут: кожну дорогу — n разів, друкуємо p50 і p99 (мс).
import time

async def bench(name, fn, n=1000):
    t = []
    for _ in range(n):
        s = time.perf_counter()
        await fn()
        t.append((time.perf_counter() - s) * 1000.0)
    t.sort()
    print(f"{name:16} p50={t[n // 2]:7.2f}  p99={t[int(n * 0.99)]:7.2f}")

# await bench("наживо",          lambda: live_read(home, mfrom, mto))
# await bench("матеріалізовано", lambda: materialized_read(home, mfrom, mto))
# await bench("кеш (влучання)",  lambda: monthly_kwh(home, month))
