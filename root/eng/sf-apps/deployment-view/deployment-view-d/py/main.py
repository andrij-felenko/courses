import random

def slow(p=0.01):                       # чи «повільний» цей листок
    return random.random() < p

def request_slow(n):                    # запит повільний, якщо ХОЧ ОДИН листок повільний
    return any(slow() for _ in range(n))

for n in (1, 10, 100):
    trials = 200_000
    frac = sum(request_slow(n) for _ in range(trials)) / trials
    print(n, round(frac, 3))            # ≈ 0.010, 0.096, 0.634 — збігається з 1 − 0.99ⁿ
