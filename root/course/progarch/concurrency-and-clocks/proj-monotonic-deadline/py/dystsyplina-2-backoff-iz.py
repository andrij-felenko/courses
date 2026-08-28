import asyncio, random

async def with_retry(op, deadline):        # deadline — момент loop.time() (МОНОТОННИЙ)
    base, cap = 0.1, 10.0
    loop, attempt = asyncio.get_running_loop(), 0
    while True:
        try:
            return await op()
        except Retryable as e:
            wait = random.uniform(0, min(cap, base * 2 ** attempt))  # повний джитер
            if loop.time() + wait > deadline:   # не спати за дедлайн
                raise TimeoutError("бюджет вичерпано") from e
            await asyncio.sleep(wait)           # asyncio.sleep — монотонний
            attempt += 1
