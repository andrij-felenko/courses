DT = 0.100          # крок інтегрування, с (стабільний таймер!)
Q = 0.0             # накопичений заряд, А·с (Кл)
cap = 7200.0        # вивчена ємність, Кл (2000 мА·год); оновлюється
i_zero = 0.0        # зсув АЦП при нульовому струмі, А


def clampf(x, lo, hi):
    return lo if x < lo else (hi if x > hi else x)


# раз на DT (з таймера/ISR): один крок лічби
def coulomb_step():
    global Q
    i = read_current_A() - i_zero               # струм зі знаком, мінус зсув нуля
    Q = clampf(Q + i * DT, 0.0, cap)            # інтеграл з обмеженням


def soc_percent():
    return 100.0 * Q / cap


# якір: термінація заряду — комірка точно повна
def on_full_charge(full_cycle):
    global Q, cap
    Q = cap                                      # SoC = 100%, дрейф обнулено
    if full_cycle:
        cap = relearn_capacity()                 # вивчення реальної ємності


# якір: відсічка розряду — комірка точно порожня
def on_cutoff():
    global Q
    Q = 0.0                                      # SoC = 0%


# напругова корекція у спокої: комірка відпочила → напруга надійна
def on_rest():
    global Q
    q_v = soc_from_ocv(read_voltage_V()) * cap   # модель/таблиця OCV→SoC
    k = 0.02                                      # м'яко: 0 < k << 1
    Q += k * (q_v - Q)                            # підтягуємо Q до напругової оцінки
