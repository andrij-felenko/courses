import random

# Терміни задач — три точки (оптимістично, найімовірніше, песимістично), у днях.
TASKS = [
    ("Міграція даних",           6, 10, 24),
    ("Інтеграція вендор-API",    4,  7, 20),
    ("Рефакторинг авторизації",  3,  5,  9),
    ("Приймальні тести",         2,  4, 12),
]

# Дискретні ризики термінів: (ймовірність, +днів якщо спрацює).
SCHED_RISKS = [
    ("Vendor-API не витягне пік", 0.30, 10),
    ("Ключова людина занедужає",  0.15,  8),
]

def betapert(o, m, p, rng, lam=4.0):
    """Одна реалізація тривалості з бета-PERT за трьома точками.
    Мода лишається рівно m; середнє — рівно (o + 4m + p)/6.
    lam=4 — класична вага моди (чому саме 4 — в анатомії PERT)."""
    if p <= o:
        return float(o)
    a = 1.0 + lam * (m - o) / (p - o)     # α:  зсув піка від o
    b = 1.0 + lam * (p - m) / (p - o)     # β:  довжина хвоста до p
    return o + (p - o) * rng.betavariate(a, b)

def trial(rng):
    """Один розіграний проєкт: сума задач + ті ризики, чия монета впала."""
    total = sum(betapert(o, m, p, rng) for _, o, m, p in TASKS)
    for _, prob, extra in SCHED_RISKS:
        if rng.random() < prob:
            total += extra
    return total

def simulate(n=100_000, seed=0):
    rng = random.Random(seed)             # фіксований seed → відтворювано
    return sorted(trial(rng) for _ in range(n))

def pct(xs, q):
    return xs[min(len(xs) - 1, int(q / 100.0 * len(xs)))]
