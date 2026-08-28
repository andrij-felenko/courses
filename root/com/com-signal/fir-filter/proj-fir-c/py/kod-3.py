QSHIFT = 15                      # формат Q15: 1.0 == 32768

class FirQ:
    def __init__(self, taps):
        self.b = list(taps)            # коефіцієнти у Q15
        self.buf = [0] * NTAPS
        self.head = 0

    def step(self, x):
        self.buf[self.head] = x

        acc = 0                        # Python int безмежний — проти переповнення
        idx = self.head
        for k in range(NTAPS):
            acc += self.b[k] * self.buf[idx]    # int16·int16 → широкий int
            idx = NTAPS - 1 if idx == 0 else idx - 1
        self.head = (self.head + 1) % NTAPS

        acc >>= QSHIFT                 # стиск Q15 назад у масштаб відліків
        if acc >  32767: acc =  32767  # насичення замість загортання
        if acc < -32768: acc = -32768
        return acc
