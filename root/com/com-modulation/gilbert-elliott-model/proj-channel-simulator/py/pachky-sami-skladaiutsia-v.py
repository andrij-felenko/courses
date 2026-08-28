from itertools import groupby
from collections import Counter

def burst_hist(channel):
    """Гістограма довжин поганих пробігів (пачок) із потоку (стан, помилка)."""
    hist = Counter()
    for bad, group in groupby(channel, key=lambda be: be[0]):
        if bad:
            hist[sum(1 for _ in group)] += 1
    return hist

h = burst_hist(gilbert_elliott(20_000_000, seed=12345))
total = sum(h.values())
mean  = sum(k * c for k, c in h.items()) / total
print(f"пачок: {total}   середня довжина: {mean:.2f}   1/r = {1/0.1:.0f}")
# пачок: 19750   середня довжина: 9.92   1/r = 10
