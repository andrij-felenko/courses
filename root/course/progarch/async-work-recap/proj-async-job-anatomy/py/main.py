LEASE = 30            # оренда клейма, секунд: довше за очікуваний прогін задачі
BASE, CAP = 2, 3600   # відступ: база 2 c, стеля — година

# full jitter (Marc Brooker, AWS, 2015): рівномірно [0, стеля), а не рівний крок
def backoff(attempts: int) -> float:
    ceiling = min(CAP, BASE * 2 ** attempts)
    return random.random() * ceiling

async def worker(pool, run):
    while alive:
        job = await claim(pool, LEASE)             # атомарний UPDATE ... SKIP LOCKED
        if job is None:
            await asyncio.sleep(0.5)               # черга без готових — перепочити
            continue
        try:
            await run(job.payload)                 # САМА робота: flash / email / …
            await complete(pool, job.id)           # стан → done
        except Exception as err:
            await fail(pool, job.id, backoff(job.attempts), str(err))  # → retry або dead
