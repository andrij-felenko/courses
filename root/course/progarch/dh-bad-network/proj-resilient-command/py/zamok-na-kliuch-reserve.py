import asyncio, time

class IdempotentExecutor:
    def __init__(self, execute, ttl=24 * 3600, now=time.monotonic):
        self._execute = execute
        self._ttl = ttl
        self._now = now
        self._done: dict[str, tuple[dict, float]] = {}      # завершені: ключ → (результат, час)
        self._inflight: dict[str, asyncio.Task] = {}        # саме в роботі: ключ → її задача

    async def handle(self, key: str, cmd: dict) -> dict:
        # 1. Уже завершене й ще свіже → віддати збережене, НЕ виконувати.
        hit = self._done.get(key)
        if hit is not None and self._now() - hit[1] < self._ttl:
            return hit[0]

        # 2. Той самий ключ уже в роботі → чекати ЙОГО задачу, не запускати другий execute.
        running = self._inflight.get(key)
        if running is not None:
            return await running

        # 3. Ми перші. Критична секція БЕЗ await: створюємо задачу й реєструємо синхронно.
        #    ensure_future ставить корутину в чергу, але НЕ запускає до найближчого await —
        #    тож між перевіркою й реєстрацією конкурент не прослизне.
        task = asyncio.ensure_future(self._run(key, cmd))
        self._inflight[key] = task
        return await task

    async def _run(self, key: str, cmd: dict) -> dict:
        try:
            result = await self._execute(cmd)               # ЄДИНЕ справжнє виконання
            self._done[key] = (result, self._now())
            return result
        finally:
            self._inflight.pop(key, None)
