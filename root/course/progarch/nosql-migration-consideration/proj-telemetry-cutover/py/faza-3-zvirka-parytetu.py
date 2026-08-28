# Вибіркова звірка: N випадкових (пристрій, вікно) — рівняємо реальні значення.
# Лічильник ловить грубу втрату рядків; вибірка — тиху псарію в самих значеннях.
def sample_parity(n=2000, window=timedelta(hours=1)):
    bad = []
    for _ in range(n):
        dev = random_device()
        lo  = random_ts(before=T0)
        old_rows = old.read(dev, lo, lo + window)         # [(ts, value), ...]
        new_rows = new.read(dev, lo, lo + window)
        if old_rows != new_rows:
            bad.append((dev, lo, len(old_rows), len(new_rows)))
    return bad          # порожньо → вибірка збіглася; є рядки → копати саме ці партиції
