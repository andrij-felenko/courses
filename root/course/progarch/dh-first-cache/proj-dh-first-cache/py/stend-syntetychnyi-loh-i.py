def synth_log(n_homes=30_000, poll_s=5, window_s=600):
    """Гарячий профіль DH: n_homes домів, кожен полить свій ключ кожні poll_s с.
    Старти розмазані по вікну → рівні ~6000 читань/с, як на живому піку."""
    events = []
    for home in range(n_homes):
        t = (home / n_homes) * poll_s          # зсув першого полінгу в межах [0, poll_s)
        while t < window_s:
            events.append((t, f"home-{home}"))
            t += poll_s
    events.sort()                              # лог іде в часовому порядку
    return events

def bench(events, ttl_s, window_s=600):
    """Прогнати лог крізь РЕАЛЬНИЙ TtlCache з фальшивим годинником.
    Повертає (влучність, QPS на джерело, загальний QPS)."""
    clock = [0.0]
    cache = TtlCache(ttl_s, now=lambda: clock[0])   # той самий кеш, лише час — наш
    hits = misses = 0
    for t, home in events:
        clock[0] = t                                 # крутимо годинник за міткою події
        if cache.get(home) is not None:
            hits += 1                                # копія свіжа — джерело не турбуємо
        else:
            misses += 1                              # промах → джерело, кладемо копію
            cache.set(home, home)
    n = hits + misses
    return hits / n, misses / window_s, n / window_s
