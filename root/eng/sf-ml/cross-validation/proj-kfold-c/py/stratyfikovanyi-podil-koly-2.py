# Крос-валідація зі стратифікованим поділом за мітками класу.
def cross_validate_stratified(n: int, k: int, num_classes: int,
                              label: list[int], seed: int) -> CVResult:
    fold_of = stratified_split(n, k, num_classes, label, seed)

    acc = [0.0] * k
    for f in range(k):
        test = [i for i in range(n) if fold_of[i] == f]        # іспит цього проходу
        train_idx = [i for i in range(n) if fold_of[i] != f]   # решта — навчання

        train(train_idx, len(train_idx))                       # знову — з нуля
        acc[f] = accuracy(test, len(test))

    mean = sum(acc) / k
    ss = sum((a - mean) ** 2 for a in acc)
    sd = math.sqrt(ss / k)

    return CVResult(mean, sd, k)
