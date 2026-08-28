# transport(addr, path, body) -> {"status": int, "body": ...};  resolve(dep) -> адреса
class ServiceClient:
    def __init__(self, dep, resolve, transport, lim):
        self._dep = dep
        self._resolve = resolve
        self._transport = transport
        self._lim = lim
        self._bulkhead = Bulkhead(lim["pool"], lim["queue"], lim["wait"])          # СВІЙ пул
        self._breaker = CircuitBreaker(lim["fails_to_open"], lim["cooldown"])       # СВІЙ запобіжник

    # Уся політика в ОДНОМУ стосі, ззовні всередину. Порядок — не косметика.
    async def call(self, path, body):
        async def attempt():
            return await with_timeout(self._lim["timeout"],                  # 4. стеля на СПРОБУ + скасування
                                      lambda: self._send(path, body))
        async def retried():
            return await with_retry(self._lim["tries"], attempt)             # 3. повтор УСЕРЕДИНІ
        return await self._bulkhead.run(                                     # 1. слот / BulkheadFull
            lambda: self._breaker.call(retried))                             # 2. відкритий? → CircuitOpen

    async def _send(self, path, body):
        addr = await self._resolve(self._dep)            # готовий екземпляр з реєстру
        res = await self._transport(addr, path, body)
        if res["status"] >= 500:
            raise Upstream5xx(res["status"])             # минуще → повтор + лічба запобіжника
        if res["status"] >= 400:
            raise Upstream4xx(res["status"])             # по суті → не повторюємо
        return res["body"]
