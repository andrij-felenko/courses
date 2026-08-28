# Ковзне середнє на кільцевому буфері (для однієї осі).
WIN = const(8)

class MovAvg:
    def __init__(self):
        self.buf = [0.0] * WIN
        self.idx = 0
        self.sum = 0.0
        self.filled = False

    def step(self, x):
        self.sum -= self.buf[self.idx]   # прибрати найстаріше
        self.buf[self.idx] = x           # покласти нове на його місце
        self.sum += x
        self.idx = (self.idx + 1) % WIN
        if self.idx == 0:
            self.filled = True
        n = WIN if self.filled else self.idx  # поки буфер не повний — ділимо на стільки, скільки є
        if n == 0:
            n = WIN
        return self.sum / n
