import asyncio, time
from concurrent.futures import ThreadPoolExecutor, ProcessPoolExecutor
# recompute_home / recompute_batch / heartbeat — ті самі, що вище

def recompute_chunk(homes) -> int:
    return recompute_batch(homes)              # шматок батчу для одного робітника

async def run(pool, label):
    asyncio.create_task(heartbeat())
    await asyncio.sleep(0.3)
    loop = asyncio.get_running_loop()
    chunks = [range(i, 2000, 4) for i in range(4)]   # 2000 домів на 4 робітники
    t0 = time.perf_counter()
    await asyncio.gather(*[loop.run_in_executor(pool, recompute_chunk, c)
                           for c in chunks])
    print(f"{label}: {(time.perf_counter()-t0)*1000:.0f} мс")
    await asyncio.sleep(0.3)

if __name__ == "__main__":
    # ПОТОКОВИЙ пул: цикл звільнено, АЛЕ GIL пускає рахувати лише одного нараз
    asyncio.run(run(ThreadPoolExecutor(max_workers=4), "4 потоки-робітники"))
    # ПРОЦЕСНИЙ пул: окремі процеси, окремі GIL — рахунок справді на всіх ядрах
    asyncio.run(run(ProcessPoolExecutor(max_workers=4), "4 процеси-робітники"))
