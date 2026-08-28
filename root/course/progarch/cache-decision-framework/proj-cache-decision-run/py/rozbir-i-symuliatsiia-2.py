def simulate(events, cls, ttl, capacity=None):
    """Cache-aside на прогоні логу: влучання ⟺ копія в кеші й ще не протухла.
    capacity=None — розмір необмежений (вирішує лише TTL); інакше LRU-витіснення
    найдавнішого. Повертає (влучність, QPS на джерело)."""
    exp = {}                       # ключ → час протухання копії
    lru = OrderedDict()            # порядок звернень для витіснення
    hits = misses = 0
    for e in events:
        if e.cls != cls:
            continue
        if e.key in exp and exp[e.key] > e.t:
            hits += 1              # копія свіжа — швидко, та, можливо, несвіже
            lru.move_to_end(e.key)
        else:
            misses += 1           # промах → до джерела, кладемо копію
            exp[e.key] = e.t + ttl
            lru[e.key] = True
            lru.move_to_end(e.key)
            if capacity and len(lru) > capacity:
                old, _ = lru.popitem(last=False)   # витісняємо найдавніший
                exp.pop(old, None)
    n = hits + misses
    return hits / n, misses / WINDOW      # влучність, QPS на джерело
