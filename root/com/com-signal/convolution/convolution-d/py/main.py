import numpy as np

# x — сигнал, h — ядро; повертає масив довжини len(x)+len(h)-1
def convolve(x, h):
    x = np.asarray(x, dtype=float)
    h = np.asarray(h, dtype=float)
    ny = len(x) + len(h) - 1
    y = np.zeros(ny)
    for m in range(ny):
        for k in range(len(x)):
            j = m - k                       # індекс ядра, біжить назустріч
            if 0 <= j < len(h):             # лише там, де ядро накриває сигнал
                y[m] += x[k] * h[j]         # помнож і додай
    return y

# на практиці той самий результат дає готова np.convolve(x, h)
