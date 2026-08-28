import numpy as np

def spectrum(x, fs, win=None):
    """Спектр дійсного сигналу: частоти в герцах, амплітуди в одиницях x."""
    N = len(x)
    w = np.ones(N) if win is None else win(N)
    X = np.fft.rfft(x * w)                 # лише додатні частоти: 0 … fs/2
    amp = 2.0 * np.abs(X) / w.sum()        # переводимо в амплітуду сигналу
    amp[0] /= 2                            # стала складова не подвоюється
    if N % 2 == 0:
        amp[-1] /= 2                       # бін Найквіста теж
    return np.fft.rfftfreq(N, 1.0/fs), amp
