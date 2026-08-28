class Service:
    def handle(self, key: str) -> str: ...

class Real(Service):
    def handle(self, key): return expensive(key)   # дорогий обрахунок

# ДО + ПІСЛЯ: заміряти час навколо делегації
class Timed(Service):
    def __init__(self, inner): self._inner = inner
    def handle(self, key):
        t0 = time.perf_counter()             # ДО
        out = self._inner.handle(key)        # делегація
        log(f"{key}: {(time.perf_counter()-t0)*1e3:.1f} ms")  # ПІСЛЯ
        return out

# ЗАМІСТЬ: на влучення кеш НЕ делегує — обриває ланцюг
class Cached(Service):
    def __init__(self, inner): self._inner = inner; self._c = {}
    def handle(self, key):
        if key in self._c:
            return self._c[key]              # обрив: назад без делегації
        out = self._inner.handle(key)        # промах → делегуємо
        self._c[key] = out
        return out

svc = Timed(Cached(Real()))
