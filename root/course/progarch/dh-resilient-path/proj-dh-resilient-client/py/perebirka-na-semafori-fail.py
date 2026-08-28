# Перебірка = семафор: ≤ limit одночасних; при переповненні або миттєва
# відмова (fail-fast, max_queue = 0), або коротке очікування в обмеженій черзі.
import asyncio
from collections import deque


class BulkheadFull(Exception):
    retryable = False


class Bulkhead:
    def __init__(self, limit, max_queue=0, max_wait=0.0):
        self._limit = limit
        self._max_queue = max_queue       # 0 → fail-fast
        self._max_wait = max_wait         # стеля очікування в черзі, с
        self._in_flight = 0
        self._waiters: deque[asyncio.Future] = deque()

    async def run(self, fn):
        await self._acquire()
        try:
            return await fn()
        finally:
            self._release()

    async def _acquire(self):
        if self._in_flight < self._limit:
            self._in_flight += 1
            return
        if len(self._waiters) >= self._max_queue:
            raise BulkheadFull()
        fut = asyncio.get_running_loop().create_future()
        self._waiters.append(fut)
        try:
            await asyncio.wait_for(fut, self._max_wait)   # паркуємось, але не назавжди
        except asyncio.TimeoutError:
            if fut in self._waiters:
                self._waiters.remove(fut)
            raise BulkheadFull()
        # слот передано нам напряму — лічильник уже враховує його

    def _release(self):
        while self._waiters:
            fut = self._waiters.popleft()
            if not fut.done():
                fut.set_result(None)     # слот ПЕРЕХОДИТЬ наступному — лічильник не чіпаємо
                return
        self._in_flight -= 1              # охочих нема — звільняємо слот
