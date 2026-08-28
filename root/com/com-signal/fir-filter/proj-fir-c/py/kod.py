NTAPS = 31                       # непарне: є центральний відвід

class FirF:
    def __init__(self, taps):
        self.b = list(taps)            # коефіцієнти (імпульсна характеристика)
        self.buf = [0.0] * NTAPS       # кільцевий буфер відліків
        self.head = 0                  # індекс найновішого відліку

    def step(self, x):
        self.buf[self.head] = x        # новий відлік у голову

        acc = 0.0
        idx = self.head
        for k in range(NTAPS):
            acc += self.b[k] * self.buf[idx]      # згортка b[k]·x[n−k]
            idx = NTAPS - 1 if idx == 0 else idx - 1   # назад по колу

        self.head = (self.head + 1) % NTAPS        # голова — вперед по колу
        return acc
