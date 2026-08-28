from dataclasses import dataclass

@dataclass
class Cache:
    value: int = 0          # збережена відповідь
    stored_at_ms: int = 0   # коли поклали в кеш
    valid: bool = False     # чи є що віддавати

# max_age_ms — контракт свіжості: наскільки застарілі дані ми ще
# згодні віддавати. Це ЧИСЛО зі сценарію атрибута, а не випадкова стала.
# Повертаємо int | None — пітонічний аналог «bool + out-параметр».
def cache_get(c: Cache, now_ms: int, max_age_ms: int) -> int | None:
    if not c.valid:
        return None                         # кеш порожній — доведеться рахувати
    if now_ms - c.stored_at_ms > max_age_ms:
        return None                         # застаріло понад дозволене — теж рахувати
    return c.value                          # свіже — швидкий шлях
