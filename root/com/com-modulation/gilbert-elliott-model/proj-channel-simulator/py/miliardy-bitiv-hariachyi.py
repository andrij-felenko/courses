import random

def channel_stats(n, p=0.001, r=0.1, e_g=0.0, e_b=0.4, seed=12345):
    """Один прохід: тільки лічильники пачок і помилок, потік не зберігаємо."""
    rng = random.Random(seed)
    bad = rng.random() < p / (p + r)          # старт зі сталого розподілу
    hist = [0] * 64                           # довжини пачок (хвіст > 63 злипаємо)
    run = errors = 0
    for _ in range(n):
        if rng.random() < (e_b if bad else e_g):
            errors += 1
        if bad:
            run += 1
        elif run:                             # поганий пробіг щойно скінчився
            hist[min(run, 63)] += 1
            run = 0
        bad = rng.random() >= r if bad else rng.random() < p
    return errors, hist
