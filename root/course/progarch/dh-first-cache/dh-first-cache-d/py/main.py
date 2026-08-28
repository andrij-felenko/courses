import time

class TtlCache:
    def __init__(self, ttl_s: float):
        self._ttl, self._store = ttl_s, {}
    def get(self, key: str):
        e = self._store.get(key)
        if not e or time.monotonic() > e[1]:        # монотонний час: TTL не зіб'є стрибок годинника
            self._store.pop(key, None); return None
        return e[0]
    def set(self, key: str, value) -> None:
        self._store[key] = (value, time.monotonic() + self._ttl)
    def invalidate(self, key: str) -> None:
        self._store.pop(key, None)

registry = TtlCache(ttl_s=5 * 60)                   # TTL 5 хв — бюджет несвіжості реєстру

async def get_registry(home_id: str) -> HomeRegistry:
    hit = registry.get(home_id)
    if hit is not None:
        return hit                                   # влучили — жодного дотику до бази
    fresh = await repo.load_registry(home_id)        # промах → джерело (переживаємо порожній кеш)
    registry.set(home_id, fresh)
    return fresh

async def rename_device(home_id: str, device_id: str, name: str) -> None:
    await repo.rename_device(home_id, device_id, name)  # джерело правди — база
    registry.invalidate(home_id)                        # наступне читання перечитає свіже

async def get_live_state(device_id: str):               # повз кеш: on/off мусить бути свіжим
    return await repo.load_state(device_id)
