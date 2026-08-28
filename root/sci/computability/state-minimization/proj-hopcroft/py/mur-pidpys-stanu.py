def moore(delta, accept):
    """Класи нерозрізнюваності уточненням розбиття. Повертає block[s]."""
    n = len(delta)
    block = [1 if s in accept else 0 for s in range(n)]
    while True:
        # підпис = (свій блок, блоки, куди ведуть переходи по кожному символі)
        sig = [(block[s], tuple(block[t] for t in delta[s])) for s in range(n)]
        ids, new = {}, [0] * n
        for s in range(n):
            new[s] = ids.setdefault(sig[s], len(ids))   # номер за першою появою
        if new == block:                                # ніщо не розкололось
            return block
        block = new
