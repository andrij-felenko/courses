# Клас факту диктує міцність читання — не система і не «всюди строго».

async def may_open(device_id: str, user_id: str) -> bool:
    # Право відчинити двері читаємо СТРОГО: авторитетне джерело (лідер/кворум).
    grant = await store.read(f"grant:{home_of(device_id)}:{user_id}", "strong")
    return bool(grant and grant.active)   # не підтвердили строго (розкол) → «ні»: fail-closed

async def latest_temp(device_id: str) -> float | None:
    # Температуру читаємо ЗРЕШТОЮ: з найближчої репліки, хай трохи застарілу.
    r = await store.read(f"temp:{device_id}", "eventual")
    return r.value if r else None         # застаріле число нікому не шкодить
