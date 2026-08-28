import random

def ge_mask(n, p=0.0003, r=0.03, e_good=0.0, e_bad=0.4, seed=7):
    """Маска помилок каналу Гілберта–Елліота вздовж n позицій ефіру.
    p: G→B (рідко), r: B→G (вихід із пачки), e_bad: густота помилок у поганому стані."""
    rng = random.Random(seed)
    bad = False
    mask = [0] * n
    runs = []                          # довжини поганих епізодів — для статистики
    run = 0
    for i in range(n):
        e = e_bad if bad else e_good
        if rng.random() < e:
            mask[i] = 1                 # канал перевернув цей біт
        if bad:
            run += 1
            if rng.random() < r:        # вибираємось із поганого стану
                bad = False; runs.append(run); run = 0
        else:
            if rng.random() < p:        # провалюємось у поганий стан
                bad = True
    if run:
        runs.append(run)
    return mask, runs
