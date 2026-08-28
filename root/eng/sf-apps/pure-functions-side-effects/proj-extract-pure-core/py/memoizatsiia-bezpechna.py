# ── Мемоізована обгортка над ЧИСТИМ ядром ────────────────────────

# ключ кеша = усе, від чого залежить результат (весь вхід ядра).
def cache_key(o: Order, p: Pricing) -> str:
    parts = [o.customer_tier,
             f"{p.tax_rate}", f"{p.free_ship_from}", f"{p.ship_cost}"]
    parts += [f"{it.price}x{it.qty}" for it in o.items]
    return "|".join(parts)

_cache: dict[str, Totals] = {}   # стан між викликами (роль C++ static)

def compute_totals_memo(order: Order, p: Pricing) -> Totals:
    key = cache_key(order, p)
    found = _cache.get(key)
    if found is not None:
        return found                          # ← влучили: віддаємо збережене

    t = compute_totals(order, p)              # промах: рахуємо ядром
    _cache[key] = t                           # і запам'ятовуємо
    return t
