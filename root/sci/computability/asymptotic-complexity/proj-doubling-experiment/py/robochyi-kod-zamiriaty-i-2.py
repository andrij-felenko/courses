import random

def total(a):                         # O(n): один прохід
    s = 0
    for x in a:
        s += x
    return s

def count_pairs(a):                   # O(n²): кожен проти кожного, повний скан
    n = len(a); c = 0
    for i in range(n):
        ai = a[i]
        for j in range(i + 1, n):
            if ai == a[j]:
                c += 1
    return c

rand     = lambda n: [random.random() for _ in range(n)]
distinct = lambda n: list(range(n))   # детермінований вхід; повний n²-скан і так гарантований

doubling(total,       rand,     100_000, 6)
doubling(count_pairs, distinct,     500, 6)
