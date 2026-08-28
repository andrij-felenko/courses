import math
from dataclasses import dataclass

# Результат крос-валідації: середнє й розкид точностей по проходах.
@dataclass
class CVResult:
    mean: float
    sd: float
    k: int

# Твої функції моделі (заглушки під конкретний алгоритм):
#   train    — навчити модель з нуля на прикладах idx[0..n-1];
#   accuracy — частка правильних на прикладах idx[0..n-1] (0..1).
# Тут — зовнішні функції, які ти реалізуєш під свій алгоритм.

# k-кратна крос-валідація над n прикладами. seed фіксує поділ.
# Повертає середнє й стандартне відхилення точностей k проходів.
def cross_validate(n: int, k: int, seed: int) -> CVResult:
    order = list(range(n))          # 0,1,2,…,n-1
    rng_seed(seed)
    shuffle(order, n)               # перемішали РАЗ наперед

    acc = [0.0] * k
    for f in range(k):
        lo = fold_start(n, k, f)
        hi = lo + fold_size(n, k, f)            # [lo, hi) — «іспитовий» блок

        test = [order[i] for i in range(n) if lo <= i < hi]        # іспит
        train_idx = [order[i] for i in range(n) if not (lo <= i < hi)]  # навч.

        train(train_idx, len(train_idx))        # НАВЧАЄМО З НУЛЯ щоразу
        acc[f] = accuracy(test, len(test))      # міряємо на відкладеному

    # середнє
    mean = sum(acc) / k
    # розкид: √( (1/k) · Σ(acc[f] − mean)² )
    ss = sum((a - mean) ** 2 for a in acc)
    sd = math.sqrt(ss / k)

    return CVResult(mean, sd, k)
