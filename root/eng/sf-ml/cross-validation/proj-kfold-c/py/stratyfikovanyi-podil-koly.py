# Стратифікований поділ n прикладів на k блоків за мітками класу.
# label[i] — клас прикладу i, значення 0..num_classes-1.
# Повертає fold_of[i] = номер блоку (0..k-1), куди потрапив приклад i.
# Пропорція класів у кожному блоці ≈ пропорція в усьому наборі.
def stratified_split(n: int, k: int, num_classes: int,
                     label: list[int], seed: int) -> list[int]:
    fold_of = [0] * n

    # buckets[c] збирає індекси прикладів класу c
    buckets = [[] for _ in range(num_classes)]
    for i in range(n):                              # розклали по відрах
        buckets[label[i]].append(i)

    rng_seed(seed)
    for c in range(num_classes):
        shuffle(buckets[c], len(buckets[c]))        # перемішали КОЖЕН клас

    # роздача по колу: приклад j класу c → блок (j % k).
    # старт кола зсуваємо на клас, щоб залишки різних класів не сідали всі в блок 0
    for c in range(num_classes):
        for j, idx in enumerate(buckets[c]):
            fold_of[idx] = (j + c) % k

    return fold_of
