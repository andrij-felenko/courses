import numpy as np

# Одним проходом: розмах і сума квадратів навколо середнього.
# Повертає (Vpp, Vrms) — розмах і True RMS у вольтах.
def measure_sine(buf, lsb_volts):             # buf: масив кодів АЦП, lsb_volts: В/код
    x = np.asarray(buf, dtype=np.float64)
    mean = x.mean()                            # рівень постійної складової в кодах

    # True RMS ЗМІННОЇ складової: віднімаємо середнє, тоді √(середнє квадратів).
    ac = x - mean                              # прибрали постамент (як AC-зв'язок)
    rms_codes = np.sqrt(np.mean(ac * ac))

    vpp  = (x.max() - x.min()) * lsb_volts
    vrms = rms_codes * lsb_volts
    return vpp, vrms
