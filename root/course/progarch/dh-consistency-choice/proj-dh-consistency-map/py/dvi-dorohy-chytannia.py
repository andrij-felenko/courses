N, W, R = 3, 2, 2                          # R + W = 4 > N = 3 → кворуми ПЕРЕТИНАЮТЬСЯ

class NoQuorum(Exception):
    ...

# СТРОГО: опитати R копій і взяти НАЙСВІЖІШУ версію серед них. Перетин кворумів
# гарантує, що серед прочитаних є копія з останнім підтвердженим записом.
def read_strong(key: str, reachable) -> Optional[Rec]:
    if len(reachable) < R:
        raise NoQuorum(f"строге читання: доступно {len(reachable)} < R={R} копій")
    best = None
    for r in reachable:
        rec = r.local(key)
        if rec and (best is None or rec.version > best.version):
            best = rec
    return best

# ЗРЕШТОЮ: одна найближча копія, без кворуму. Доступно навіть у розкол,
# але віддає те, що ця копія знає зараз, — хай і застаріле.
def read_eventual(key: str, local: Replica) -> Optional[Rec]:
    return local.local(key)

# Ворота доступу читають право СТРОГО; будь-який сумнів (нема кворуму) → «ні».
def may_open(key: str, reachable) -> bool:
    try:
        grant = read_strong(key, reachable)
        return bool(grant and grant.value is True)       # нема запису / active=False → ні
    except NoQuorum:
        return False                                     # fail-closed: за сумніву — замкнено

# Телеметрію читаємо ЗРЕШТОЮ — застаріле число нікому не шкодить.
def latest_temp(key: str, local: Replica):
    r = read_eventual(key, local)
    return r.value if r else None
