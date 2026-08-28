import numpy as np

# Частота через підрахунок висхідних переходів рівня mean із гістерезисом.
# Повертає Гц; NaN, якщо переходів замало для оцінки.
def measure_freq(buf, mean, hyst_codes, fs):
    x = np.asarray(buf, dtype=np.float64) - mean   # прибрали постамент
    armed = True                                   # готові ловити висхідний перехід
    first_cross = last_cross = None                # індекси відліків (дробові)
    cycles = 0
    prev = x[0]
    for i in range(1, len(x)):
        cur = x[i]
        if armed and prev < 0.0 and cur >= 0.0:    # перетин нуля вгору
            # лінійно уточнюємо момент перетину між відліками (менша похибка)
            frac = prev / (prev - cur)             # 0..1 між i-1 та i
            cross = (i - 1) + frac
            if first_cross is None:
                first_cross = cross
            else:
                last_cross = cross
                cycles += 1
            armed = False                          # гістерезис: чекаємо спаду
        elif cur < -hyst_codes:
            armed = True                           # впали нижче −h → знову готові
        prev = cur
    if cycles == 0:
        return float("nan")                        # менше двох переходів
    period_samples = (last_cross - first_cross) / cycles  # відліків на період
    return fs / period_samples                     # Гц
