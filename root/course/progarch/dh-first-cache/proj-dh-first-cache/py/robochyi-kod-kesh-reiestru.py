import asyncio, time
from dataclasses import dataclass
from typing import Protocol, Callable

# ── Порт: звужений зріз DeviceRepository з DH v3 (реєстр + живий стан) ──
@dataclass(frozen=True)
class Device:
    id: str; name: str; room: str; kind: str

@dataclass(frozen=True)
class HomeRegistry:
    home_id: str; plan: str; threshold: float; devices: list[Device]

@dataclass(frozen=True)
class LiveState:
    device_id: str; on: bool; celsius: float

class DeviceRepository(Protocol):
    async def load_registry(self, home_id: str) -> HomeRegistry: ...   # повільний зріз — кешуємо
    async def load_state(self, device_id: str) -> LiveState: ...       # живий зріз — повз кеш
    async def rename_device(self, home_id: str, device_id: str, name: str) -> None: ...
    async def pair_device(self, home_id: str, d: Device) -> None: ...

# ── TTL-кеш зі ВСТАВНИМ годинником (щоб тести й стенд кермували часом) ──
class TtlCache:
    def __init__(self, ttl_s: float, now: Callable[[], float] = time.monotonic):
        self._ttl, self._now, self._store = ttl_s, now, {}
    def get(self, key: str):
        e = self._store.get(key)
        if e is None:
            return None
        if self._now() >= e[1]:                 # протухла → прибрати й повідомити про промах
            self._store.pop(key, None); return None
        return e[0]
    def set(self, key: str, value) -> None:
        self._store[key] = (value, self._now() + self._ttl)
    def invalidate(self, key: str) -> None:
        self._store.pop(key, None)
    def __len__(self) -> int:
        return len(self._store)

# ── Кеш реєстру: cache-aside + закликання + скид-на-запис, ПОВЕРХ того самого порту ──
class CachedRegistry:
    def __init__(self, inner: DeviceRepository, ttl_s: float, now=time.monotonic):
        self._inner = inner
        self._cache = TtlCache(ttl_s, now)
        self._inflight: dict[str, asyncio.Task] = {}   # рейси в польоті (один на ключ)
        self.loads = 0                                  # скільки читань дійшло до джерела

    async def load_registry(self, home_id: str) -> HomeRegistry:
        hit = self._cache.get(home_id)
        if hit is not None:
            return hit                            # влучили — джерело не турбуємо
        task = self._inflight.get(home_id)
        if task is None:                          # ПЕРШИЙ промах заводить рейс…
            task = asyncio.create_task(self._fill(home_id))
            self._inflight[home_id] = task        # синхронно, до першого await → гонки нема
        return await task                         # …решта чекають на той самий рейс

    async def _fill(self, home_id: str) -> HomeRegistry:
        try:
            self.loads += 1
            fresh = await self._inner.load_registry(home_id)   # промах → джерело (переживаємо порожнечу)
            self._cache.set(home_id, fresh)
            return fresh
        finally:
            self._inflight.pop(home_id, None)                  # рейс завершено — прибрати слот

    async def load_state(self, device_id: str) -> LiveState:   # повз кеш: on/off і °C мусять бути свіжі
        return await self._inner.load_state(device_id)

    async def rename_device(self, home_id, device_id, name) -> None:
        await self._inner.rename_device(home_id, device_id, name)  # спершу джерело правди — база…
        self._cache.invalidate(home_id)                           # …тоді скид: наступне читання свіже

    async def pair_device(self, home_id, d: Device) -> None:
        await self._inner.pair_device(home_id, d)                 # спарювання додало пристрій…
        self._cache.invalidate(home_id)                           # …стара копія реєстру протухла
