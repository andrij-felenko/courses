import asyncio

class PolicyProvider:                          # PolicySource: .policy() -> Policy (без I/O)
    def __init__(self, src, interval_s=30.0):
        self._src = src                        # .pull(since_rev)->bundle|None; .verify(bundle)->bool
        self._interval = interval_s
        self._current = None                   # None, доки не прийшов перший валідний бандл
        self._revision = ""

    def policy(self):
        if self._current is None:
            raise RuntimeError("policy-not-loaded")   # старт без правила: нема чому дозволяти
        return self._current                          # читання вказівника — без I/O

    async def refresh_once(self):
        bundle = await self._src.pull(self._revision)
        if bundle is None:
            return                             # 304: нема нового — лишаємо чинне
        if not self._src.verify(bundle):
            return                             # підпис не зійшовся → НЕ активуємо
        self._current = compile_policy(bundle) # атомарна підміна вказівника
        self._revision = bundle.version

    async def run(self):                       # фонова задача: asyncio.create_task(provider.run())
        while True:
            try:
                await self.refresh_once()
            except Exception:
                pass                           # збій тягання → тримаємо старе (fail-static)
            await asyncio.sleep(self._interval)
