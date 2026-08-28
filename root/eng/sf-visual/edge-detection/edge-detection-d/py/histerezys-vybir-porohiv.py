# Поріг за процентилем сили: T_high такий, що вище нього — верхні (1-keep) пікселів.
# keep, напр., 0.7 → відсікаємо верхні 30% як «сильні кандидати». Сила в [0..maxmag).
def high_threshold_by_percentile(mag, maxmag, keep):
    hist = [0] * maxmag
    for m in mag:
        if m >= maxmag:
            m = maxmag - 1                    # захист від виходу за гістограму
        hist[m] += 1
    target = keep * len(mag)                  # стільки лишаємо НИЖЧЕ порога
    acc = 0
    for t in range(maxmag):                   # йдемо від слабких угору
        acc += hist[t]
        if acc >= target:                     # тут накопичили keep частку
            return t                          # T_high; T_low беремо як t/2..t/3
    return maxmag
