from collections import deque

# Ковзне середнє на кільцевому буфері (для однієї осі).
WIN = 8

class MovAvg:
    def __init__(self):
        self.buf = deque([0.0] * WIN, maxlen=WIN)  # найстаріше саме випадає
        self.sum = 0.0
        self.filled = False
        self.count = 0

    def step(self, x):
        oldest = self.buf[0] if len(self.buf) == WIN else 0.0
        self.sum -= oldest          # прибрати найстаріше
        self.buf.append(x)          # покласти нове на його місце
        self.sum += x
        if self.count < WIN:
            self.count += 1
        n = self.count              # поки буфер не повний — ділимо на стільки, скільки є
        return self.sum / n
