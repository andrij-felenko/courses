import math
import time

ADC_FS    = 3.3      # повна шкала АЦП, В
ADC_MAX   = 4095.0   # 12-бітний АЦП
SETTLE_MS = 50       # > 5·τ кола (тут τ ≈ 160 мкс для f_c=1 кГц)
WINDOW    = 2000     # скільки вибірок беремо на одну точку

# зовнішні примітиви плати (MicroPython на тому самому МК):
#   gen_set_freq(hz) — перелаштувати DDS/ШІМ-генератор
#   time.sleep_ms(ms) — затримка
#   adc_read(ch)     — одна вибірка, у вольтах

# розмах (peak-to-peak) каналу за вікно вибірок
def measure_pp(ch):
    vmin, vmax = ADC_FS, 0.0
    for _ in range(WINDOW):
        v = adc_read(ch)
        if v < vmin: vmin = v
        if v > vmax: vmax = v
    return vmax - vmin                 # подвоєна амплітуда

# одна точка АЧХ: повертає підсилення в децибелах
def bode_point(f):
    gen_set_freq(f)                    # крок 1: частота змінилась…
    time.sleep_ms(SETTLE_MS)           # крок 2: …дати колу встановитися
    a_in  = measure_pp(0)              # крок 3: CH0 — вхід кола
    a_out = measure_pp(1)              #         CH1 — вихід кола
    return 20.0 * math.log10(a_out / a_in)  # крок 4: відношення → дБ

def bode_sweep(f_min, f_max, per_decade):
    mult = 10.0 ** (1.0 / per_decade)  # лог-крок: рівний множник
    f = f_min
    while f <= f_max * 1.001:
        g = bode_point(f)
        print("%8.1f Hz   %+6.1f dB" % (f, g))  # у файл/UART → у графік
        f *= mult
