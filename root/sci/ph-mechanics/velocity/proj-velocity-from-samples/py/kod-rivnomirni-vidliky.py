from collections import deque


class Slope:
    def __init__(self, n, dt):
        assert n % 2 == 1, "вікно має бути непарним"
        self.m = (n - 1) // 2
        self.k = list(range(-self.m, self.m + 1))          # ваги −M … M
        self.sumk2 = self.m * (self.m + 1) * (2 * self.m + 1) // 3
        self.inv_dt = 1.0 / dt
        self.buf = deque(maxlen=n)                          # кільце сам-по-собі

    def push(self, x):
        self.buf.append(x)                                 # найновіший — праворуч
        if len(self.buf) < self.buf.maxlen:
            return 0.0                                      # вікно ще не повне
        # deque іде від найстарішого до найновішого — рівно як k = −M … M
        num = sum(ki * xi for ki, xi in zip(self.k, self.buf))
        return num / self.sumk2 * self.inv_dt              # оцінка в центрі вікна
