import asyncio, time

def recompute_home(seed: int) -> int:
    # справжній CPU: прокрутити правила одного дому, жодного вводу-виводу
    acc = seed & 0xFFFFFFFF
    for r in range(200):                       # ~200 правил на дім
        acc = (acc * 1_000_003 + r) & 0xFFFFFFFF
        for _ in range(64):                    # трохи «м'яса» на кожне правило
            acc ^= (acc << 13) & 0xFFFFFFFF
            acc ^= acc >> 17
            acc ^= (acc << 5) & 0xFFFFFFFF
    return acc

def recompute_batch(homes) -> int:
    return sum(recompute_home(h) for h in homes)

async def heartbeat():
    prev = time.perf_counter()
    while True:
        await asyncio.sleep(0.01)              # хочемо тік кожні 10 мс
        gap = (time.perf_counter() - prev) * 1000
        if gap > 50:                           # пропущені тіки — одразу видно
            print(f"  ⚠ серцебиття спізнилось на {gap:.0f} мс")
        prev = time.perf_counter()

async def main():
    asyncio.create_task(heartbeat())
    await asyncio.sleep(0.3)                   # рівне серцебиття…
    t0 = time.perf_counter()
    recompute_batch(range(2000))               # ❌ синхронно В ОБРОБНИКУ — морозить цикл
    print(f"батч у циклі: {(time.perf_counter()-t0)*1000:.0f} мс")
    await asyncio.sleep(0.3)

asyncio.run(main())
